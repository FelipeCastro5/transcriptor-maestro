from datetime import datetime
from sqlalchemy import Column, String, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Acuerdo(Base):
    __tablename__ = "acuerdos"

    id = Column(String(36), primary_key=True)  # Ej: AC-8A1C92
    reunion_id = Column(String(36), ForeignKey("reuniones.id", ondelete="CASCADE"), nullable=False)
    responsable_id = Column(String(36), ForeignKey("responsables.id", ondelete="SET NULL"), nullable=True)
    responsable_crudo = Column(String(150), nullable=True)  # Lo que extrajo la IA antes de Fuzzy Matching
    responsable = Column(String(150), nullable=False)       # Nombre resuelto/canónico
    similitud_fuzzy = Column(Float, default=1.0)           # Score de Levenshtein (0.0 a 1.0)
    tarea_desc = Column(Text, nullable=False)
    fecha_compromiso = Column(String(100), nullable=True)
    fecha_limite = Column(Date, nullable=True)
    fragmento_original = Column(Text, nullable=False)      # Cita textual exacta (auditoría anti-sesgo)
    estado = Column(String(20), default="pendiente", nullable=False)  # pendiente, completado, atrasado
    acuerdo_origen_id = Column(String(36), ForeignKey("acuerdos.id", ondelete="SET NULL"), nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    reunion = relationship("Reunion", back_populates="acuerdos")
    responsable_rel = relationship("Responsable", back_populates="acuerdos")
    historial = relationship("HistorialEstado", back_populates="acuerdo", cascade="all, delete-orphan")
