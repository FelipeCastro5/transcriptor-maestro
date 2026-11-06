from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Query, Path, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.schemas.response import ResponseDto, ResponseUtil
from app.schemas.alerta import AlertaResponse, BarridoResultadoResponse, SchedulerStatusResponse
from app.services.storage_service import storage_service
from app.services.alert_service import alert_service
from app.core.scheduler import system_scheduler
from app.db.session import get_db

router = APIRouter()

# ---------------------------------------------------------------------------
# ALMACENAMIENTO Y CACHÉ
# ---------------------------------------------------------------------------

@router.get(
    "/estado-cache",
    response_model=ResponseDto[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Verificar contenido del almacenamiento temporal (Caché)",
    description="Permite inspeccionar si existen archivos temporales pendientes de limpiar, su conteo y peso total en MB."
)
async def verificar_estado_cache():
    diagnostico = storage_service.obtener_estado_storage()
    mensaje = (
        f"Se encontraron {diagnostico['total_archivos']} archivo(s) temporal(es) ({diagnostico['total_tamano_mb']} MB) listos para limpiar."
        if diagnostico["tiene_contenido"]
        else "El almacenamiento temporal está limpio. No hay archivos pendientes."
    )
    return ResponseUtil.success(data=diagnostico, message=mensaje)


@router.post(
    "/limpiar-cache",
    response_model=ResponseDto[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Limpiar archivos temporales manualmente",
    description="Elimina de forma manual los audios temporales y salidas generadas de reuniones pasadas."
)
async def ejecutar_limpieza_cache(
    solo_audios: bool = Query(False, description="Si es True, purga únicamente la carpeta de audios temporales"),
    solo_salidas: bool = Query(False, description="Si es True, purga únicamente las salidas (txt, md, json)")
):
    resultado = storage_service.limpiar_todo(solo_audios=solo_audios, solo_salidas=solo_salidas)
    mensaje = f"Limpieza completada: {resultado['archivos_eliminados']} archivo(s) eliminados ({resultado['tamano_liberado_mb']} MB liberados)."
    return ResponseUtil.success(data=resultado, message=mensaje)


# ---------------------------------------------------------------------------
# SISTEMA DE ALERTAS (INTELIGENCIA INTERPERSONAL)
# ---------------------------------------------------------------------------

@router.get(
    "/alertas",
    response_model=ResponseDto[List[AlertaResponse]],
    status_code=status.HTTP_200_OK,
    summary="Listar alertas emitidas por el sistema",
    description="Retorna las alertas automáticas de acuerdos atrasados, omisiones y eventos de resiliencia VACAS."
)
async def listar_alertas(
    solo_no_leidas: bool = Query(False, description="Filtrar solo alertas pendientes de revisar"),
    limite: int = Query(50, description="Número máximo de alertas a retornar"),
    db: Session = Depends(get_db)
):
    alertas = alert_service.listar_alertas(db=db, solo_no_leidas=solo_no_leidas, limite=limite)
    data = [AlertaResponse.model_validate(a) for a in alertas]
    return ResponseUtil.success(data=data, message=f"Se obtuvieron {len(data)} alertas.")


@router.post(
    "/alertas/{id_alerta}/marcar-leida",
    response_model=ResponseDto[AlertaResponse],
    status_code=status.HTTP_200_OK,
    summary="Marcar alerta como leída / atendida"
)
async def marcar_alerta_leida(
    id_alerta: str = Path(..., description="ID de la alerta a marcar"),
    db: Session = Depends(get_db)
):
    alerta = alert_service.marcar_como_leida(db=db, alerta_id=id_alerta)
    if not alerta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Alerta '{id_alerta}' no encontrada.")
    return ResponseUtil.success(data=AlertaResponse.model_validate(alerta), message="Alerta marcada como leída.")


# ---------------------------------------------------------------------------
# CURVA DE CONTROL DE ESPACIOS IGUALES (SCHEDULER AUTÓNOMO)
# ---------------------------------------------------------------------------

@router.get(
    "/scheduler/estado",
    response_model=ResponseDto[SchedulerStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar estado de la Curva de Espacios Iguales (Scheduler)"
)
async def obtener_estado_scheduler():
    info = system_scheduler.get_info()
    return ResponseUtil.success(data=SchedulerStatusResponse(**info), message="Estado del scheduler obtenido exitosamente.")


@router.post(
    "/scheduler/ejecutar",
    response_model=ResponseDto[BarridoResultadoResponse],
    status_code=status.HTTP_200_OK,
    summary="Forzar ejecución manual del barrido de medianoche",
    description="Ejecuta de inmediato la Curva de Espacios Iguales para recalcular atrasos y detectar omisiones ante el jurado."
)
async def forzar_barrido_scheduler():
    resultado = system_scheduler.ejecutar_inmediato()
    return ResponseUtil.success(
        data=BarridoResultadoResponse(**resultado),
        message=resultado.get("mensaje", "Barrido completado.")
    )
