from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, status

from app.schemas.response import ResponseDto, ResponseUtil
from app.services.storage_service import storage_service

router = APIRouter()


@router.get(
    "/estado-cache",
    response_model=ResponseDto[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Verificar contenido del almacenamiento temporal (Caché)",
    description="Permite inspeccionar si existen archivos temporales (audios subidos y reportes generados) pendientes de limpiar, su conteo y peso total en MB."
)
async def verificar_estado_cache():
    """
    Retorna el estado de los directorios storage/audios_temp y storage/salidas.
    """
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
    description="Elimina de forma manual los audios temporales y salidas generadas de reuniones pasadas, preservando los archivos .gitkeep de control de versiones."
)
async def ejecutar_limpieza_cache(
    solo_audios: bool = Query(False, description="Si es True, purga únicamente la carpeta de audios temporales"),
    solo_salidas: bool = Query(False, description="Si es True, purga únicamente las salidas (txt, md, json)")
):
    """
    Ejecuta la purga de almacenamiento temporal a demanda.
    """
    resultado = storage_service.limpiar_todo(solo_audios=solo_audios, solo_salidas=solo_salidas)
    mensaje = f"Limpieza completada: {resultado['archivos_eliminados']} archivo(s) eliminados ({resultado['tamano_liberado_mb']} MB liberados)."
    return ResponseUtil.success(data=resultado, message=mensaje)
