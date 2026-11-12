from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.acuerdo import AcuerdoResponse

class EstadoReunion(str, Enum):
    EN_COLA = "EN_COLA"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"
    CANCELADO = "CANCELADO"

class EstrategiaIA(int, Enum):
    ESTRATEGIA_1_REGLAS_OFFLINE = 1
    ESTRATEGIA_2_HUGGINGFACE_OPEN = 2
    ESTRATEGIA_3_DEEPSEEK_BASE = 3
    ESTRATEGIA_4_PROMPT_AVANZADO = 4
    ESTRATEGIA_5_HIBRIDO_MADURO = 5

class ReunionUploadResponse(BaseModel):
    id_reunion: str = Field(..., description="Identificador único de la reunión")
    nombre_archivo: str = Field(..., description="Nombre original del archivo subido")
    tamano_mb: float = Field(..., description="Tamaño del archivo en Megabytes")
    estado: EstadoReunion = Field(default=EstadoReunion.EN_COLA, description="Estado inicial del trabajo")
    mensaje: str = Field(default="Audio recibido y encolado correctamente")

class ReunionEstadoResponse(BaseModel):
    id_reunion: str
    nombre_archivo: str
    estado: EstadoReunion
    progreso_estimado: Optional[str] = "Pendiente de procesamiento"
    fecha_registro: datetime
    fecha_actualizacion: datetime
    error_detalle: Optional[str] = None

class ReunionResumen(BaseModel):
    id_reunion: str
    nombre_archivo: str
    estado: EstadoReunion
    duracion_segundos: Optional[float] = None
    resumen_ejecutivo: Optional[str] = None
    total_acuerdos: int = 0

class ReunionDetalleResponse(BaseModel):
    id_reunion: str
    nombre_archivo: str
    tamano_mb: Optional[float] = None
    duracion_segundos: Optional[float] = None
    estado: EstadoReunion
    progreso_estimado: Optional[str] = None
    estrategia_utilizada: Optional[EstrategiaIA] = None
    tiempo_procesamiento_seg: Optional[float] = None
    transcripcion: Optional[str] = None
    resumen_ejecutivo: Optional[str] = None
    acuerdos: List[AcuerdoResponse] = Field(default_factory=list)
    metadatos_audio: Dict[str, Any] = Field(default_factory=dict)
    auditoria_logs: List[Dict[str, Any]] = Field(default_factory=list)
    fecha_registro: datetime
    fecha_actualizacion: datetime
    error_detalle: Optional[str] = None

class ProcesarReunionRequest(BaseModel):
    estrategia: EstrategiaIA = Field(
        default=EstrategiaIA.ESTRATEGIA_5_HIBRIDO_MADURO,
        description="Estrategia del Handler Dinámico a utilizar (1 a 5)"
    )
    modo_consenso: bool = Field(
        default=False,
        description="Activa el modo de consenso concurrente dual (DeepSeek + OpenAI) con cálculo de discrepancia entre modelos"
    )
