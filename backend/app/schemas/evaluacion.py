from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CalibrarWERRequest(BaseModel):
    reunion_id: Optional[str] = Field(None, description="ID de la reunión a evaluar (opcional si se pasa texto_hipotesis)")
    texto_referencia: str = Field(..., description="Texto Ground Truth (patrón de oro humano)")
    texto_hipotesis: Optional[str] = Field(None, description="Texto transcrito por Whisper (opcional si se provee reunion_id)")
    modelo_evaluado: str = Field("whisper-medium", description="Nombre del modelo Whisper evaluado")

class AlineacionToken(BaseModel):
    ref: Optional[str] = None
    hyp: Optional[str] = None
    op: str = Field(..., description="MATCH, SUBSTITUTION, INSERTION, DELETION")
    peso: float = 1.0

class CalibrarWERResponse(BaseModel):
    id: str
    reunion_id: Optional[str] = None
    modelo_evaluado: str
    total_palabras_gt: int
    total_palabras_hyp: int
    sustituciones: int
    eliminaciones: int
    inserciones: int
    aciertos: int
    wer: float
    wer_porcentaje: float
    wer_ponderado: float
    wer_ponderado_porcentaje: float
    precision_palabra: float
    precision_palabra_porcentaje: float
    longitud_relativa: float
    estado_calidad: str
    cumple_meta_sprint: bool
    alineacion: List[AlineacionToken] = []
    creado_en: Optional[datetime] = None

    class Config:
        from_attributes = True

class DataDriftRequest(BaseModel):
    texto: Optional[str] = Field(None, description="Texto de transcripción para análisis léxico")
    reunion_id: Optional[str] = Field(None, description="ID de reunión a analizar")
    vocabulario_adicional: Optional[List[str]] = Field(None, description="Términos adicionales para la base léxica")

class DataDriftResponse(BaseModel):
    total_palabras_evaluadas: int
    palabras_unicas_evaluadas: int
    tamano_vocabulario_base: int
    palabras_oov_detectadas: List[str]
    total_palabras_oov: int
    ratio_oov: float
    ratio_oov_porcentaje: float
    estado_drift: str
    alerta_drift: bool
    recomendacion: str

class PromptVersionResponse(BaseModel):
    id: str
    version: str
    nombre: str
    descripcion: str
    hash_md5: str
    modelos_compatibles: List[str]
    es_activo: bool
    prompt_sistema: str
    creado_en: str

class ActivarPromptRequest(BaseModel):
    version_id: str

