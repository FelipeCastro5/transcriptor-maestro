from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.auditoria import AuditoriaIALog
from app.db.models.reunion import Reunion
from app.db.models.evaluacion import EvaluacionCalibracion
from app.core.perceptron import perceptron, NivelError, EstadoBinario
from app.core.prompt_registry import prompt_registry
from app.services.vacas import vacas_manager
from app.services.eval_service import eval_service
from app.schemas.response import ResponseDto, ResponseUtil
from app.schemas.evaluacion import (
    CalibrarWERRequest, CalibrarWERResponse,
    DataDriftRequest, DataDriftResponse,
    PromptVersionResponse, ActivarPromptRequest
)

router = APIRouter()

class AuditoriaLogResponse(BaseModel):
    id: str
    reunion_id: str
    etapa: str
    proveedor: str
    estado_binario: int
    nivel_error: int
    latencia_ms: Optional[int] = None
    conmutacion_vaca: bool
    creado_en: datetime

    class Config:
        from_attributes = True

class EstadoProveedoresResponse(BaseModel):
    perceptron_activo: bool = True
    vaca_primaria: str = vacas_manager.PROVEEDOR_PRIMARIO
    vaca_replica: str = vacas_manager.PROVEEDOR_REPLICA
    vaca_emergencia: str = vacas_manager.PROVEEDOR_EMERGENCIA
    simulacion_fallo_activa: bool
    sla_latencia_maxima_ms: int = perceptron.LATENCIA_MAXIMA_MS

class SimularFalloRequest(BaseModel):
    activar_fallo: bool = True

@router.get(
    "/estado",
    response_model=ResponseDto[EstadoProveedoresResponse],
    summary="Estado de salud del Perceptrón y cadena de VACAS",
    description="Retorna el estado operativo de los proveedores de LLM y si la simulación de fallo está activa."
)
async def get_estado_auditoria():
    data = EstadoProveedoresResponse(
        perceptron_activo=True,
        vaca_primaria=vacas_manager.PROVEEDOR_PRIMARIO,
        vaca_replica=vacas_manager.PROVEEDOR_REPLICA,
        vaca_emergencia=vacas_manager.PROVEEDOR_EMERGENCIA,
        simulacion_fallo_activa=vacas_manager.simular_fallo_primaria,
        sla_latencia_maxima_ms=perceptron.LATENCIA_MAXIMA_MS
    )
    return ResponseUtil.success(data=data, message="Estado operativo del Perceptrón obtenido exitosamente")

@router.get(
    "/metricas",
    response_model=ResponseDto[Dict[str, Any]],
    summary="Métricas consolidadas de auditoría de IA",
    description="Calcula la tasa de éxito (estados binarios 0/1), promedio de latencia y total de conmutaciones VACA."
)
async def get_metricas_auditoria(db: Session = Depends(get_db)):
    data = perceptron.obtener_metricas_globales(db)
    return ResponseUtil.success(data=data, message="Métricas de telemetría calculadas exitosamente")

@router.get(
    "/logs",
    response_model=ResponseDto[List[AuditoriaLogResponse]],
    summary="Consultar historial de telemetría y auditoría de IA",
    description="Retorna los registros de ejecución almacenados por el Perceptrón en PostgreSQL."
)
async def get_logs_auditoria(
    reunion_id: Optional[str] = Query(None, description="Filtrar por ID de reunión"),
    limite: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AuditoriaIALog)
    if reunion_id:
        query = query.filter(AuditoriaIALog.reunion_id == reunion_id)
    logs = query.order_by(AuditoriaIALog.creado_en.desc()).limit(limite).all()
    data = [AuditoriaLogResponse.model_validate(log) for log in logs]
    return ResponseUtil.success(data=data, message=f"Se obtuvieron {len(data)} registros de auditoría")

@router.post(
    "/simular-conmutacion",
    response_model=ResponseDto[Dict[str, Any]],
    summary="Simular caída del LLM Primario (Chaos Engineering)",
    description="Fuerza un fallo en la VACA Primaria para verificar la conmutación en caliente hacia la VACA réplica."
)
async def simular_fallo(body: SimularFalloRequest):
    vacas_manager.simular_fallo_primaria = body.activar_fallo
    data = {
        "mensaje": f"Simulación de caída de VACA Primaria {'ACTIVADA' if body.activar_fallo else 'DESACTIVADA'}",
        "simulacion_activa": vacas_manager.simular_fallo_primaria
    }
    return ResponseUtil.success(
        data=data,
        message=f"Modo Chaos Testing {'activado' if body.activar_fallo else 'desactivado'}"
    )

# ============================================================================
# ENDPOINTS MLOPS FASE 2: CALIBRACIÓN WER, DATA DRIFT Y PROMPT REGISTRY
# ============================================================================

@router.post(
    "/calibrar-wer",
    response_model=ResponseDto[CalibrarWERResponse],
    summary="Calibrar y evaluar WER / WER ponderado en vivo (MLOps)",
    description="Ejecuta la alineación Levenshtein palabra por palabra entre Ground Truth y la hipótesis de ASR, computando WER, WER_w, S, D, I, H y Precisión."
)
async def calibrar_wer(body: CalibrarWERRequest, db: Session = Depends(get_db)):
    hyp_texto = body.texto_hipotesis

    # Si no se pasó texto pero sí un ID de reunión, extraer transcripción de la base de datos
    if not hyp_texto and body.reunion_id:
        reunion = db.query(Reunion).filter(Reunion.id == body.reunion_id).first()
        if not reunion or not reunion.transcripcion_texto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró transcripción registrada para la reunión {body.reunion_id}"
            )
        hyp_texto = reunion.transcripcion_texto

    if not hyp_texto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe suministrar texto_hipotesis o un reunion_id con transcripción válida."
        )

    try:
        resultado = eval_service.calcular_wer(
            texto_referencia=body.texto_referencia,
            texto_hipotesis=hyp_texto,
            modelo_evaluado=body.modelo_evaluado,
            reunion_id=body.reunion_id,
            db=db
        )
        return ResponseUtil.success(
            data=resultado,
            message=f"Calibración WER completada exitosamente ({resultado['estado_calidad']})."
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error durante el cálculo de WER: {str(e)}")

@router.get(
    "/calibraciones",
    response_model=ResponseDto[List[Dict[str, Any]]],
    summary="Historial de calibraciones de transcripción",
    description="Retorna las evaluaciones de WER y calibración de modelos ejecutadas y registradas en PostgreSQL."
)
async def listar_calibraciones(limite: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    registros = db.query(EvaluacionCalibracion).order_by(EvaluacionCalibracion.creado_en.desc()).limit(limite).all()
    data = [
        {
            "id": r.id,
            "reunion_id": r.reunion_id,
            "modelo_evaluado": r.modelo_evaluado,
            "total_palabras_gt": r.total_palabras_gt,
            "total_palabras_hyp": r.total_palabras_hyp,
            "sustituciones": r.sustituciones,
            "eliminaciones": r.eliminaciones,
            "inserciones": r.inserciones,
            "aciertos": r.aciertos,
            "wer": r.wer,
            "wer_porcentaje": round(r.wer * 100, 2),
            "wer_ponderado": r.wer_ponderado,
            "wer_ponderado_porcentaje": round(r.wer_ponderado * 100, 2),
            "precision_palabra": r.precision_palabra,
            "precision_palabra_porcentaje": round(r.precision_palabra * 100, 2),
            "longitud_relativa": r.longitud_relativa,
            "estado_calidad": r.estado_calidad,
            "creado_en": r.creado_en
        }
        for r in registros
    ]
    return ResponseUtil.success(data=data, message=f"Se obtuvieron {len(data)} calibraciones históricas.")

@router.post(
    "/data-drift",
    response_model=ResponseDto[DataDriftResponse],
    summary="Análisis de Data Drift Léxico en Transcripciones",
    description="Detecta términos fuera de vocabulario (OOV) y evalúa el nivel de desviación lingüística de la conversación."
)
async def analizar_data_drift(body: DataDriftRequest, db: Session = Depends(get_db)):
    texto = body.texto
    if not texto and body.reunion_id:
        reunion = db.query(Reunion).filter(Reunion.id == body.reunion_id).first()
        if reunion and reunion.transcripcion_texto:
            texto = reunion.transcripcion_texto

    if not texto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe suministrar texto o un reunion_id con transcripción válida."
        )

    analisis = eval_service.analizar_data_drift(
        texto=texto,
        vocabulario_adicional=body.vocabulario_adicional,
        db=db
    )
    return ResponseUtil.success(
        data=analisis,
        message=f"Análisis de Data Drift ejecutado: Estado {analisis['estado_drift']}"
    )

@router.get(
    "/prompts-historial",
    response_model=ResponseDto[List[PromptVersionResponse]],
    summary="Catálogo y Registro de Versiones de Prompts (Prompt Registry)",
    description="Retorna las versiones de prompts gestionadas, sus hashes MD5 inmutables y la versión activa en producción."
)
async def get_prompts_historial():
    prompts = prompt_registry.listar_prompts()
    return ResponseUtil.success(data=prompts, message="Catálogo de prompts obtenido exitosamente.")

@router.post(
    "/prompts-activar",
    response_model=ResponseDto[Dict[str, Any]],
    summary="Activar Versión de Prompt en Caliente",
    description="Cambia dinámicamente la versión activa de prompt utilizada por el motor de inferencia LLM."
)
async def activar_prompt_version(body: ActivarPromptRequest):
    exito = prompt_registry.activar_version(body.version_id)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el prompt con ID '{body.version_id}'"
        )
    activo = prompt_registry.obtener_prompt_activo()
    return ResponseUtil.success(
        data=activo.to_dict(),
        message=f"Versión de prompt '{activo.version}' ({activo.nombre}) activada en caliente."
    )
