import time
from enum import IntEnum
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.auditoria import AuditoriaIALog

class NivelError(IntEnum):
    NIVEL_0_CATASTROFICO = 0   # Fallo total de infraestructura o de todos los proveedores
    NIVEL_1_CRITICO = 1        # Fallo de API primaria (HTTP 5xx, timeout, JSON inválido)
    NIVEL_2_MEDIO = 2          # Formato de fechas o entidades con ambigüedad
    NIVEL_3_LEVE = 3           # Desviación fonética en nombre resuelta por Fuzzy Matching
    NIVEL_4_INFORMATIVO = 4    # Ejecución dentro del SLA (< 3000ms) sin incidencias

class EstadoBinario(IntEnum):
    EXITO = 0
    FALLO = 1

class PerceptronAuditor:
    """
    El Perceptrón (Megatron):
    Auditor salvavidas del sistema que monitorea tiempos de respuesta (SLA),
    clasifica errores en la jerarquía 0-4, registra estados binarios (0/1)
    y supervisa la conmutación de contingencia entre LLMs (VACAS).
    """

    LATENCIA_MAXIMA_MS: int = 3000  # SLA de 3 segundos definido en los documentos maestros

    @classmethod
    def clasificar_ejecucion(cls, latencia_ms: int, fallo_proveedor: bool, conmutacion_activada: bool) -> tuple[int, int]:
        """
        Retorna (estado_binario, nivel_error) según los parámetros de telemetría.
        """
        if fallo_proveedor and conmutacion_activada:
            # Hubo fallo en la primaria pero la réplica VACA salvó la ejecución
            return EstadoBinario.FALLO.value, NivelError.NIVEL_1_CRITICO.value

        if fallo_proveedor and not conmutacion_activada:
            # Fallo irrecuperable
            return EstadoBinario.FALLO.value, NivelError.NIVEL_0_CATASTROFICO.value

        if latencia_ms > cls.LATENCIA_MAXIMA_MS:
            # Excedió el SLA de 3 segundos
            return EstadoBinario.EXITO.value, NivelError.NIVEL_2_MEDIO.value

        return EstadoBinario.EXITO.value, NivelError.NIVEL_4_INFORMATIVO.value

    @classmethod
    def registrar_log(
        cls,
        db: Session,
        reunion_id: str,
        etapa: str,
        proveedor: str,
        latencia_ms: int,
        estado_binario: int = 0,
        nivel_error: int = 4,
        conmutacion_vaca: bool = False
    ) -> AuditoriaIALog:
        """
        Inserta un registro de auditoría en la tabla auditoria_ia_logs de PostgreSQL.
        """
        try:
            nuevo_log = AuditoriaIALog(
                reunion_id=reunion_id,
                etapa=etapa,
                proveedor=proveedor,
                estado_binario=estado_binario,
                nivel_error=nivel_error,
                latencia_ms=latencia_ms,
                conmutacion_vaca=conmutacion_vaca
            )
            db.add(nuevo_log)
            db.commit()
            db.refresh(nuevo_log)
            return nuevo_log
        except Exception as e:
            db.rollback()
            print(f"[PERCEPTRON-ERROR] No se pudo guardar el log de auditoría: {e}")
            raise e

    @classmethod
    def obtener_metricas_globales(cls, db: Session) -> Dict[str, Any]:
        """
        Calcula las métricas consolidadas del Perceptrón.
        """
        total = db.query(AuditoriaIALog).count()
        if total == 0:
            return {
                "total_ejecuciones": 0,
                "tasa_exito_porcentaje": 100.0,
                "tasa_conmutacion_vaca_porcentaje": 0.0,
                "latencia_promedio_ms": 0,
                "total_conmutaciones_vaca": 0,
                "alertas_sla": 0
            }

        exitos = db.query(AuditoriaIALog).filter(AuditoriaIALog.estado_binario == 0).count()
        conmutaciones = db.query(AuditoriaIALog).filter(AuditoriaIALog.conmutacion_vaca == True).count()
        promedio_latencia = db.query(func.avg(AuditoriaIALog.latencia_ms)).scalar() or 0
        alertas_sla = db.query(AuditoriaIALog).filter(AuditoriaIALog.latencia_ms > cls.LATENCIA_MAXIMA_MS).count()

        return {
            "total_ejecuciones": total,
            "tasa_exito_porcentaje": round((exitos / total) * 100, 2),
            "tasa_conmutacion_vaca_porcentaje": round((conmutaciones / total) * 100, 2),
            "latencia_promedio_ms": int(promedio_latencia),
            "total_conmutaciones_vaca": conmutaciones,
            "alertas_sla": alertas_sla
        }

perceptron = PerceptronAuditor()
