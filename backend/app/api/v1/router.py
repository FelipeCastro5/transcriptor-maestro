from fastapi import APIRouter
from app.api.v1.endpoints import reuniones, acuerdos, responsables, auditoria, sistema

api_router = APIRouter()
api_router.include_router(reuniones.router, prefix="/reuniones", tags=["Reuniones"])
api_router.include_router(acuerdos.router, prefix="/acuerdos", tags=["Acuerdos y Compromisos"])
api_router.include_router(responsables.router, prefix="/responsables", tags=["Responsables (Fuzzy Matching)"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["Auditoría y Resiliencia (Perceptrón & VACAS)"])
api_router.include_router(sistema.router, prefix="/sistema", tags=["Sistema y Mantenimiento (Caché & Storage)"])
