from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AlertaResponse(BaseModel):
    id: str = Field(..., description="Identificador único de la alerta (ej: ALT-8A1C92)")
    proyecto_id: Optional[str] = None
    reunion_id: Optional[str] = None
    acuerdo_id: Optional[str] = None
    tipo_alerta: str = Field(..., description="Tipo: ATRASO, OMISION, SLA_EXCEDIDO, VACA_FAILOVER, DATA_DRIFT")
    nivel_severidad: str = Field(..., description="Severidad: INFO, WARNING, CRITICAL")
    titulo: str
    mensaje: str
    leida: bool
    webhook_enviado: bool
    creada_en: datetime

    class Config:
        from_attributes = True

class BarridoResultadoResponse(BaseModel):
    acuerdos_revisados: int
    acuerdos_atrasados: int
    omisiones_detectadas: int
    alertas_generadas: int
    mensaje: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SchedulerStatusResponse(BaseModel):
    activo: bool
    proxima_ejecucion: Optional[datetime] = None
    intervalo_minutos: int
    total_alertas_activas: int
    modo: str = "DEMOSTRACION_CONTINUA"

