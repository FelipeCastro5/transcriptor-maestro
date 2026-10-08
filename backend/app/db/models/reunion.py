from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Reunion(Base):
    __tablename__ = "reuniones"

    id = Column(String(36), primary_key=True)  # Ej: MEET-8F18F681
    proyecto_id = Column(String(36), ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True)
    nombre_archivo = Column(String(255), nullable=False)
    ruta_audio = Column(String(500), nullable=False)
    tamano_mb = Column(Float, nullable=True)
    duracion_seg = Column(Float, nullable=True)
    estado_proceso = Column(String(20), default="EN_COLA", nullable=False)
    estrategia_ia = Column(Integer, default=5)
    transcripcion_texto = Column(Text, nullable=True)
    resumen_ejecutivo = Column(Text, nullable=True)
    tiempo_procesamiento_seg = Column(Float, nullable=True)
    metadatos_audio = Column(JSON, default=dict)
    error_detalle = Column(Text, nullable=True)
    progreso_estimado = Column(String(255), default="Audio recibido")
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="reuniones")
    acuerdos = relationship("Acuerdo", back_populates="reunion", cascade="all, delete-orphan")
    auditoria_logs = relationship("AuditoriaIALog", back_populates="reunion", cascade="all, delete-orphan")
