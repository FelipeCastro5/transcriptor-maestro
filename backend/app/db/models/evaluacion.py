import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON
from app.db.base import Base

class EvaluacionCalibracion(Base):
    __tablename__ = "evaluaciones_calibracion"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reunion_id = Column(String(36), ForeignKey("reuniones.id", ondelete="SET NULL"), nullable=True)
    modelo_evaluado = Column(String(50), default="whisper-medium")
    total_palabras_gt = Column(Integer, nullable=False)
    total_palabras_hyp = Column(Integer, nullable=False)
    sustituciones = Column(Integer, default=0)
    eliminaciones = Column(Integer, default=0)
    inserciones = Column(Integer, default=0)
    aciertos = Column(Integer, default=0)
    wer = Column(Float, nullable=False)
    wer_ponderado = Column(Float, nullable=False)
    precision_palabra = Column(Float, nullable=False)
    longitud_relativa = Column(Float, nullable=False)
    data_drift_ratio = Column(Float, default=0.0)
    estado_calidad = Column(String(50), default="OPTIMO")  # OPTIMO, ACEPTABLE, CRITICO
    detalles_alineacion = Column(JSON, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

