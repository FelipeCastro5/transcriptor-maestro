from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class EstadoAcuerdo(str, Enum):
    PENDIENTE = "pendiente"
    COMPLETADO = "completado"
    ATRASADO = "atrasado"

class AcuerdoBase(BaseModel):
    tarea_desc: str = Field(..., description="Descripción clara de la tarea pactada")
    responsable: str = Field(..., description="Nombre canónico del responsable asignado tras Fuzzy Matching")
    responsable_crudo: Optional[str] = Field(None, description="Texto original inferido por la IA antes de corrección")
    similitud_fuzzy: Optional[float] = Field(1.0, description="Puntuación de coincidencia de Levenshtein (0.0 a 1.0)")
    fecha_compromiso: Optional[str] = Field(None, description="Fecha o plazo límite mencionado")
    fragmento_original: str = Field(..., description="Cita exacta de la conversación donde se acordó la tarea")
    estado: EstadoAcuerdo = Field(default=EstadoAcuerdo.PENDIENTE, description="Estado actual del compromiso")

class AcuerdoCreate(AcuerdoBase):
    id_reunion: str
    responsable_id: Optional[str] = None

class AcuerdoResponse(AcuerdoBase):
    id_acuerdo: str = Field(..., description="ID del acuerdo")
    id_reunion: str = Field(..., description="ID de la reunión")
    responsable_id: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class AcuerdoUpdateEstado(BaseModel):
    estado: EstadoAcuerdo = Field(..., description="Nuevo estado del compromiso")
    nota_actualizacion: Optional[str] = Field(None, description="Observaciones o notas sobre la actualización")
