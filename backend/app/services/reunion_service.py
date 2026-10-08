import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Any
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.db.models.reunion import Reunion
from app.db.models.acuerdo import Acuerdo
from app.db.models.responsable import Responsable
from app.db.models.historial import HistorialEstado
from app.schemas.reunion import EstadoReunion, EstrategiaIA
from app.schemas.acuerdo import EstadoAcuerdo
from app.services.ai_handler import ai_handler
from app.services.matching import fuzzy_matcher

class ReunionService:
    def __init__(self):
        init_db()

    def guardar_audio(self, file: UploadFile, proyecto_id: str = "PROJ-DEFAULT") -> dict:
        nombre_original = file.filename or "audio_desconocido"
        extension = Path(nombre_original).suffix.lower()

        if extension not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato no permitido ({extension}). Formatos válidos: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )

        id_reunion = f"MEET-{uuid.uuid4().hex[:8].upper()}"
        nombre_guardado = f"{id_reunion}{extension}"
        destino = settings.full_upload_path / nombre_guardado

        try:
            with open(destino, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al escribir archivo en disco: {str(e)}"
            )

        tamano_bytes = destino.stat().st_size
        tamano_mb = round(tamano_bytes / (1024 * 1024), 2)

        if tamano_mb > settings.MAX_AUDIO_SIZE_MB:
            destino.unlink(missing_ok=True)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo supera el límite de {settings.MAX_AUDIO_SIZE_MB}MB"
            )

        ahora = datetime.utcnow()
        
        db: Session = SessionLocal()
        try:
            nueva_reunion = Reunion(
                id=id_reunion,
                proyecto_id=proyecto_id,
                nombre_archivo=nombre_original,
                ruta_audio=str(destino),
                tamano_mb=tamano_mb,
                estado_proceso=EstadoReunion.EN_COLA.value,
                progreso_estimado="Audio recibido y encolado.",
                creado_en=ahora,
                actualizado_en=ahora
            )
            db.add(nueva_reunion)
            db.commit()
            db.refresh(nueva_reunion)
            
            return {
                "id_reunion": id_reunion,
                "nombre_archivo": nombre_original,
                "ruta_archivo": str(destino),
                "tamano_mb": tamano_mb,
                "estado": EstadoReunion.EN_COLA,
                "progreso_estimado": nueva_reunion.progreso_estimado,
                "fecha_registro": ahora,
                "fecha_actualizacion": ahora
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error guardando en base de datos: {e}")
        finally:
            db.close()

    def procesar_tarea_segundo_plano(self, id_reunion: str, estrategia: EstrategiaIA):
        db: Session = SessionLocal()
        try:
            reunion = db.query(Reunion).filter(Reunion.id == id_reunion).first()
            if not reunion:
                return

            reunion.estado_proceso = EstadoReunion.PROCESANDO.value
            reunion.progreso_estimado = f"Transcribiendo y analizando con Estrategia {estrategia.value}..."
            reunion.actualizado_en = datetime.utcnow()
            db.commit()

            # 1. Ejecución del Handler de IA (Transcripción + LLM con auditoría del Perceptrón)
            resultado = ai_handler.procesar_reunion(
                id_reunion=id_reunion,
                nombre_archivo=reunion.nombre_archivo,
                ruta_audio=reunion.ruta_audio,
                estrategia=estrategia,
                db=db
            )

            catalogo = db.query(Responsable).filter(Responsable.activo == True).all()

            for ac in resultado["acuerdos"]:
                nombre_crudo = ac.get("responsable", "No asignado")
                resp_obj, nombre_oficial, score = fuzzy_matcher.emparejar_responsable(
                    nombre_crudo=nombre_crudo,
                    catalogo_responsables=catalogo,
                    umbral=settings.FUZZY_THRESHOLD
                )

                id_ac = ac.get("id_acuerdo") or f"AC-{uuid.uuid4().hex[:6].upper()}"
                nuevo_acuerdo = Acuerdo(
                    id=id_ac,
                    reunion_id=id_reunion,
                    responsable_id=resp_obj.id if resp_obj else None,
                    responsable_crudo=nombre_crudo,
                    responsable=nombre_oficial,
                    similitud_fuzzy=score,
                    tarea_desc=ac["tarea_desc"],
                    fecha_compromiso=ac.get("fecha_compromiso"),
                    fragmento_original=ac["fragmento_original"],
                    estado="pendiente",
                    creado_en=datetime.utcnow(),
                    actualizado_en=datetime.utcnow()
                )
                db.add(nuevo_acuerdo)

            acuerdos_previos_pendientes = db.query(Acuerdo).filter(
                Acuerdo.reunion_id != id_reunion,
                Acuerdo.estado == "pendiente"
            ).all()

            cierres_detectados = fuzzy_matcher.detectar_cumplimiento_historico(
                transcripcion=resultado["transcripcion"],
                acuerdos_pendientes=acuerdos_previos_pendientes
            )

            for cierre in cierres_detectados:
                ac_previo = db.query(Acuerdo).filter(Acuerdo.id == cierre["acuerdo_id"]).first()
                if ac_previo:
                    historial = HistorialEstado(
                        acuerdo_id=ac_previo.id,
                        reunion_origen_id=id_reunion,
                        estado_anterior=ac_previo.estado,
                        estado_nuevo="completado",
                        evidencia_texto=cierre["motivo"]
                    )
                    ac_previo.estado = "completado"
                    ac_previo.actualizado_en = datetime.utcnow()
                    db.add(historial)
                    print(f"[HISTORIAL] Acuerdo previo {ac_previo.id} ('{ac_previo.tarea_desc}') actualizado a COMPLETADO.")

            reunion.estado_proceso = EstadoReunion.COMPLETADO.value
            reunion.progreso_estimado = "Procesamiento finalizado con éxito."
            reunion.transcripcion_texto = resultado["transcripcion"]
            reunion.resumen_ejecutivo = resultado["resumen_ejecutivo"]
            reunion.tiempo_procesamiento_seg = resultado["tiempo_procesamiento_seg"]
            reunion.estrategia_ia = estrategia.value
            reunion.actualizado_en = datetime.utcnow()
            db.commit()

        except Exception as e:
            db.rollback()
            reunion = db.query(Reunion).filter(Reunion.id == id_reunion).first()
            if reunion:
                reunion.estado_proceso = EstadoReunion.FALLIDO.value
                reunion.progreso_estimado = "Fallo en procesamiento de IA"
                reunion.error_detalle = str(e)
                reunion.actualizado_en = datetime.utcnow()
                db.commit()
            print(f"[ERROR] Error procesando reunion {id_reunion}: {e}")
        finally:
            db.close()

    def obtener_estado(self, id_reunion: str) -> Optional[dict]:
        db: Session = SessionLocal()
        try:
            r = db.query(Reunion).filter(Reunion.id == id_reunion).first()
            if not r:
                return None
            return {
                "id_reunion": r.id,
                "nombre_archivo": r.nombre_archivo,
                "estado": EstadoReunion(r.estado_proceso),
                "progreso_estimado": r.progreso_estimado,
                "fecha_registro": r.creado_en,
                "fecha_actualizacion": r.actualizado_en,
                "error_detalle": r.error_detalle
            }
        finally:
            db.close()

    def obtener_detalle(self, id_reunion: str) -> Optional[dict]:
        db: Session = SessionLocal()
        try:
            r = db.query(Reunion).filter(Reunion.id == id_reunion).first()
            if not r:
                return None

            acuerdos = db.query(Acuerdo).filter(Acuerdo.reunion_id == id_reunion).all()
            
            acuerdos_list = []
            for a in acuerdos:
                acuerdos_list.append({
                    "id_acuerdo": a.id,
                    "id_reunion": a.reunion_id,
                    "responsable_id": a.responsable_id,
                    "responsable_crudo": a.responsable_crudo,
                    "responsable": a.responsable,
                    "similitud_fuzzy": a.similitud_fuzzy,
                    "tarea_desc": a.tarea_desc,
                    "fecha_compromiso": a.fecha_compromiso,
                    "fragmento_original": a.fragmento_original,
                    "estado": EstadoAcuerdo(a.estado),
                    "fecha_creacion": a.creado_en
                })

            return {
                "id_reunion": r.id,
                "nombre_archivo": r.nombre_archivo,
                "estado": EstadoReunion(r.estado_proceso),
                "progreso_estimado": r.progreso_estimado,
                "estrategia_utilizada": EstrategiaIA(r.estrategia_ia) if r.estrategia_ia else None,
                "tiempo_procesamiento_seg": r.tiempo_procesamiento_seg,
                "transcripcion": r.transcripcion_texto,
                "resumen_ejecutivo": r.resumen_ejecutivo,
                "acuerdos": acuerdos_list,
                "fecha_registro": r.creado_en,
                "fecha_actualizacion": r.actualizado_en,
                "error_detalle": r.error_detalle
            }
        finally:
            db.close()

    def listar_reuniones(self) -> List[dict]:
        db: Session = SessionLocal()
        try:
            reuniones = db.query(Reunion).order_by(Reunion.creado_en.desc()).all()
            resultado = []
            for r in reuniones:
                total_acuerdos = db.query(Acuerdo).filter(Acuerdo.reunion_id == r.id).count()
                resultado.append({
                    "id_reunion": r.id,
                    "nombre_archivo": r.nombre_archivo,
                    "estado": EstadoReunion(r.estado_proceso),
                    "resumen_ejecutivo": r.resumen_ejecutivo,
                    "total_acuerdos": total_acuerdos
                })
            return resultado
        finally:
            db.close()

    def listar_acuerdos(self, id_reunion: Optional[str] = None) -> List[dict]:
        db: Session = SessionLocal()
        try:
            query = db.query(Acuerdo)
            if id_reunion:
                query = query.filter(Acuerdo.reunion_id == id_reunion)
            acuerdos = query.order_by(Acuerdo.creado_en.desc()).all()
            
            return [
                {
                    "id_acuerdo": a.id,
                    "id_reunion": a.reunion_id,
                    "responsable_id": a.responsable_id,
                    "responsable_crudo": a.responsable_crudo,
                    "responsable": a.responsable,
                    "similitud_fuzzy": a.similitud_fuzzy,
                    "tarea_desc": a.tarea_desc,
                    "fecha_compromiso": a.fecha_compromiso,
                    "fragmento_original": a.fragmento_original,
                    "estado": EstadoAcuerdo(a.estado),
                    "fecha_creacion": a.creado_en
                }
                for a in acuerdos
            ]
        finally:
            db.close()

    def actualizar_estado_acuerdo(self, id_acuerdo: str, nuevo_estado: EstadoAcuerdo, nota: Optional[str] = None) -> Optional[dict]:
        db: Session = SessionLocal()
        try:
            acuerdo = db.query(Acuerdo).filter(Acuerdo.id == id_acuerdo).first()
            if not acuerdo:
                return None

            estado_anterior = acuerdo.estado
            acuerdo.estado = nuevo_estado.value
            acuerdo.actualizado_en = datetime.utcnow()

            historial = HistorialEstado(
                acuerdo_id=acuerdo.id,
                reunion_origen_id=acuerdo.reunion_id,
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado.value,
                evidencia_texto=nota or "Actualización manual vía API"
            )
            db.add(historial)
            db.commit()
            db.refresh(acuerdo)

            return {
                "id_acuerdo": acuerdo.id,
                "id_reunion": acuerdo.reunion_id,
                "responsable_id": acuerdo.responsable_id,
                "responsable_crudo": acuerdo.responsable_crudo,
                "responsable": acuerdo.responsable,
                "similitud_fuzzy": acuerdo.similitud_fuzzy,
                "tarea_desc": acuerdo.tarea_desc,
                "fecha_compromiso": acuerdo.fecha_compromiso,
                "fragmento_original": acuerdo.fragmento_original,
                "estado": EstadoAcuerdo(acuerdo.estado),
                "fecha_creacion": acuerdo.creado_en
            }
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Error actualizando acuerdo: {e}")
            return None
        finally:
            db.close()

reunion_service = ReunionService()
