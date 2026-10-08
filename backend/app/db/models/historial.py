import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class HistorialEstado(Base):
    __tablename__ = "historial_estados"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    acuerdo_id = Column(String(36), ForeignKey("acuerdos.id", ondelete="CASCADE"), nullable=False)
    reunion_origen_id = Column(String(36), ForeignKey("reuniones.id", ondelete="SET NULL"), nullable=True)
    estado_anterior = Column(String(20), nullable=False)
    estado_nuevo = Column(String(20), nullable=False)
    evidencia_texto = Column(Text, nullable=True)
    fecha_cambio = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    acuerdo = relationship("Acuerdo", back_populates="historial")
