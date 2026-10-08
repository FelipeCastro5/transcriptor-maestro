from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.auditoria import AuditoriaIALog
from app.core.perceptron import perceptron, NivelError, EstadoBinario
from app.services.vacas import vacas_manager
from app.schemas.response import ResponseDto, ResponseUtil

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
