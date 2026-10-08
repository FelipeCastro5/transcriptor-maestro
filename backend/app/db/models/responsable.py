import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Responsable(Base):
    __tablename__ = "responsables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proyecto_id = Column(String(36), ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True)
    nombre_completo = Column(String(150), nullable=False)
    alias_conocidos = Column(JSON, default=list)  # Ej: ["Juan", "Juancho", "Juna", "Pérez"]
    email = Column(String(150), nullable=True)
    rol = Column(String(50), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    proyecto = relationship("Proyecto", back_populates="responsables")
    acuerdos = relationship("Acuerdo", back_populates="responsable_rel")
