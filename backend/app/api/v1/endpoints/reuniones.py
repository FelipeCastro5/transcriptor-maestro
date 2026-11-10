from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Query, BackgroundTasks, HTTPException, status
from app.schemas.reunion import (
    ReunionUploadResponse,
    ReunionEstadoResponse,
    ReunionResumen,
    ReunionDetalleResponse,
    ProcesarReunionRequest,
    EstrategiaIA
)
from app.schemas.response import ResponseDto, ResponseUtil
from app.services.reunion_service import reunion_service

router = APIRouter()

@router.post(
    "/upload",
    response_model=ResponseDto[ReunionUploadResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Subir archivo de audio de reunión",
    description="Recibe un archivo de audio, lo valida, almacena y opcionalmente inicia su procesamiento con Whisper y LLM en segundo plano.",
    responses={
        202: {"description": "Audio aceptado y encolado para procesamiento"},
        400: {"description": "Formato de audio no válido"},
        413: {"description": "Archivo supera el límite de tamaño"},
        422: {"description": "Error de validación en parámetros"},
        500: {"description": "Error al guardar o procesar archivo"}
    }
)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    procesar_inmediato: bool = Query(True, description="Si es True, inicia la transcripción y extracción automáticamente"),
    estrategia: EstrategiaIA = Query(EstrategiaIA.ESTRATEGIA_5_HIBRIDO_MADURO, description="Estrategia del Handler a ejecutar"),
    modelo_whisper: str = Query("medium", description="Modelo Whisper a usar (small, medium, large)"),
    llm_preferido: str = Query("deepseek", description="LLM preferido (deepseek, openai)"),
    modelo_llm: str = Query("deepseek-chat", description="Modelo de LLM específico (ej. deepseek-chat, gpt-4o-mini)"),
    modo_consenso: bool = Query(False, description="Activa el modo de consenso dual (DeepSeek + OpenAI concurrente)")
):
    registro = reunion_service.guardar_audio(file)
    id_reunion = registro["id_reunion"]

    if procesar_inmediato:
        background_tasks.add_task(
            reunion_service.procesar_tarea_segundo_plano,
            id_reunion=id_reunion,
            estrategia=estrategia,
            modelo_whisper=modelo_whisper,
            llm_preferido=llm_preferido,
            modelo_llm=modelo_llm,
            modo_consenso=modo_consenso
        )

    data = ReunionUploadResponse(
        id_reunion=id_reunion,
        nombre_archivo=registro["nombre_archivo"],
        tamano_mb=registro["tamano_mb"],
        estado=registro["estado"],
        mensaje="Audio recibido. Procesamiento en segundo plano iniciado." if procesar_inmediato else "Audio recibido y almacenado."
    )
    return ResponseUtil.accepted(
        data=data,
        message="Audio recibido y encolado para procesamiento asíncrono"
    )

@router.post(
    "/{id_reunion}/procesar",
    response_model=ResponseDto[ReunionEstadoResponse],
    summary="Disparar procesamiento manual de una reunión",
    description="Permite ejecutar o re-ejecutar el pipeline de análisis seleccionando una estrategia específica (1 a 5).",
    responses={
        200: {"description": "Operación exitosa"},
        400: {"description": "Solicitud inválida o archivo no soportado"},
        404: {"description": "Recurso no encontrado"},
        413: {"description": "Entidad solicitada demasiado grande (ej. archivo > 250MB)"},
        422: {"description": "Error de validación en los datos enviados"},
        500: {"description": "Error interno del servidor"}
    }
)
async def procesar_reunion(
    id_reunion: str,
    body: ProcesarReunionRequest,
    background_tasks: BackgroundTasks,
    modelo_whisper: str = Query("medium", description="Modelo Whisper a usar (small, medium, large)"),
    llm_preferido: str = Query("deepseek", description="LLM preferido (deepseek, openai)"),
    modelo_llm: str = Query("deepseek-chat", description="Modelo de LLM específico (ej. deepseek-chat, gpt-4o-mini)")
):
    registro = reunion_service.obtener_estado(id_reunion)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reunión '{id_reunion}' no encontrada"
        )

    background_tasks.add_task(
        reunion_service.procesar_tarea_segundo_plano,
        id_reunion=id_reunion,
        estrategia=body.estrategia,
        modelo_whisper=modelo_whisper,
        llm_preferido=llm_preferido,
        modelo_llm=modelo_llm,
        modo_consenso=body.modo_consenso
    )

    data = ReunionEstadoResponse(
        id_reunion=registro["id_reunion"],
        nombre_archivo=registro["nombre_archivo"],
        estado=registro["estado"],
        progreso_estimado=f"Iniciando procesamiento con Estrategia {body.estrategia.value}...",
        fecha_registro=registro["fecha_registro"],
        fecha_actualizacion=registro["fecha_actualizacion"],
        error_detalle=registro.get("error_detalle")
    )
    return ResponseUtil.success(
        data=data,
        message=f"Procesamiento con Estrategia {body.estrategia.value} encolado exitosamente"
    )

@router.get(
    "/{id_reunion}/estado",
    response_model=ResponseDto[ReunionEstadoResponse],
    summary="Consultar estado de procesamiento de una reunión",
    responses={
        200: {"description": "Operación exitosa"},
        400: {"description": "Solicitud inválida o archivo no soportado"},
        404: {"description": "Recurso no encontrado"},
        413: {"description": "Entidad solicitada demasiado grande (ej. archivo > 250MB)"},
        422: {"description": "Error de validación en los datos enviados"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_estado_reunion(id_reunion: str):
    registro = reunion_service.obtener_estado(id_reunion)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reunión '{id_reunion}' no encontrada"
        )
    data = ReunionEstadoResponse(
        id_reunion=registro["id_reunion"],
        nombre_archivo=registro["nombre_archivo"],
        estado=registro["estado"],
        progreso_estimado=registro.get("progreso_estimado"),
        fecha_registro=registro["fecha_registro"],
        fecha_actualizacion=registro["fecha_actualizacion"],
        error_detalle=registro.get("error_detalle")
    )
    return ResponseUtil.success(data=data, message="Estado de reunión obtenido exitosamente")

@router.post(
    "/{id_reunion}/cancelar",
    response_model=ResponseDto[ReunionEstadoResponse],
    summary="Cancelar el procesamiento en curso de una reunión",
    description="Detiene el procesamiento de una reunión en estado EN_COLA o PROCESANDO, limpia archivos temporales y transiciona su estado a CANCELADO.",
    responses={
        200: {"description": "Procesamiento cancelado exitosamente"},
        404: {"description": "Reunión no encontrada"},
        500: {"description": "Error interno del servidor"}
    }
)
async def cancelar_reunion(id_reunion: str):
    registro = reunion_service.cancelar_reunion(id_reunion)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reunión '{id_reunion}' no encontrada"
        )
    data = ReunionEstadoResponse(
        id_reunion=registro["id_reunion"],
        nombre_archivo=registro["nombre_archivo"],
        estado=registro["estado"],
        progreso_estimado=registro.get("progreso_estimado"),
        fecha_registro=registro["fecha_registro"],
        fecha_actualizacion=registro["fecha_actualizacion"],
        error_detalle=registro.get("error_detalle")
    )
    return ResponseUtil.success(data=data, message="Procesamiento cancelado exitosamente")

@router.get(
    "/{id_reunion}/resultados",
    response_model=ResponseDto[ReunionDetalleResponse],
    summary="Obtener resultados completos de la reunión",
    description="Retorna la transcripción íntegra, el resumen ejecutivo y el listado de acuerdos detectados.",
    responses={
        200: {"description": "Operación exitosa"},
        400: {"description": "Solicitud inválida o archivo no soportado"},
        404: {"description": "Recurso no encontrado"},
        413: {"description": "Entidad solicitada demasiado grande (ej. archivo > 250MB)"},
        422: {"description": "Error de validación en los datos enviados"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_resultados_reunion(id_reunion: str):
    detalle = reunion_service.obtener_detalle(id_reunion)
    if not detalle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reunión '{id_reunion}' no encontrada"
        )
    data = ReunionDetalleResponse(**detalle)
    return ResponseUtil.success(data=data, message="Resultados de la reunión obtenidos exitosamente")

@router.get(
    "/",
    response_model=ResponseDto[List[ReunionResumen]],
    summary="Listar todas las reuniones registradas",
    responses={
        200: {"description": "Operación exitosa"},
        400: {"description": "Solicitud inválida o archivo no soportado"},
        404: {"description": "Recurso no encontrado"},
        413: {"description": "Entidad solicitada demasiado grande (ej. archivo > 250MB)"},
        422: {"description": "Error de validación en los datos enviados"},
        500: {"description": "Error interno del servidor"}
    }
)
async def list_reuniones():
    reuniones_raw = reunion_service.listar_reuniones()
    data = [ReunionResumen(**r) for r in reuniones_raw]
    return ResponseUtil.success(data=data, message="Catálogo de reuniones obtenido exitosamente")
