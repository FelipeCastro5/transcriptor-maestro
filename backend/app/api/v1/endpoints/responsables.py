from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.responsable import Responsable
from app.schemas.responsable import ResponsableResponse, ResponsableCreate
from app.schemas.response import ResponseDto, ResponseUtil

router = APIRouter()

@router.get(
    "/",
    response_model=ResponseDto[List[ResponsableResponse]],
    summary="Listar catálogo de miembros del equipo (Responsables)",
    description="Retorna los responsables contra los cuales se realiza el Fuzzy Matching de nombres."
)
async def list_responsables(db: Session = Depends(get_db)):
    responsables = db.query(Responsable).filter(Responsable.activo == True).all()
    data = [ResponsableResponse.model_validate(r) for r in responsables]
    return ResponseUtil.success(data=data, message="Catálogo de responsables obtenido exitosamente")

@router.post(
    "/",
    response_model=ResponseDto[ResponsableResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo miembro del equipo",
    description="Permite agregar nuevos integrantes y sus alias para que la IA los reconozca automáticamente."
)
async def create_responsable(body: ResponsableCreate, db: Session = Depends(get_db)):
    nuevo = Responsable(
        proyecto_id=body.proyecto_id,
        nombre_completo=body.nombre_completo,
        alias_conocidos=body.alias_conocidos,
        email=body.email,
        rol=body.rol,
        activo=body.activo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    data = ResponsableResponse.model_validate(nuevo)
    return ResponseUtil.created(data=data, message="Responsable registrado exitosamente")
