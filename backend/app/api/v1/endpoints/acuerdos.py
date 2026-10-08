from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.acuerdo import AcuerdoResponse, AcuerdoUpdateEstado
from app.schemas.response import ResponseDto, ResponseUtil
from app.services.reunion_service import reunion_service

router = APIRouter()

@router.get(
    "/",
    response_model=ResponseDto[List[AcuerdoResponse]],
    summary="Listar todos los acuerdos",
    description="Permite consultar todos los compromisos y tareas registradas en el sistema, con filtro opcional por reunión."
)
async def list_acuerdos(
    id_reunion: Optional[str] = Query(None, description="Filtrar acuerdos pertenecientes a una reunión específica")
):
    acuerdos = reunion_service.listar_acuerdos(id_reunion=id_reunion)
    data = [AcuerdoResponse(**a) for a in acuerdos]
    return ResponseUtil.success(data=data, message="Acuerdos obtenidos exitosamente")

@router.get(
    "/reunion/{id_reunion}",
    response_model=ResponseDto[List[AcuerdoResponse]],
    summary="Obtener acuerdos de una reunión en específico"
)
async def get_acuerdos_por_reunion(id_reunion: str):
    acuerdos = reunion_service.listar_acuerdos(id_reunion=id_reunion)
    data = [AcuerdoResponse(**a) for a in acuerdos]
    return ResponseUtil.success(data=data, message=f"Acuerdos de la reunión {id_reunion} obtenidos exitosamente")

@router.patch(
    "/{id_acuerdo}/estado",
    response_model=ResponseDto[AcuerdoResponse],
    summary="Actualizar estado de un acuerdo",
    description="Permite cambiar el estado de un compromiso a 'pendiente', 'completado' o 'atrasado'."
)
async def update_estado_acuerdo(id_acuerdo: str, body: AcuerdoUpdateEstado):
    acuerdo_actualizado = reunion_service.actualizar_estado_acuerdo(
        id_acuerdo=id_acuerdo,
        nuevo_estado=body.estado,
        nota=body.nota_actualizacion
    )
    if not acuerdo_actualizado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Acuerdo con ID '{id_acuerdo}' no encontrado"
        )
    data = AcuerdoResponse(**acuerdo_actualizado)
    return ResponseUtil.success(data=data, message=f"Estado del acuerdo actualizado a '{body.estado.value}'")
