import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    reuniones = relationship("Reunion", back_populates="proyecto", cascade="all, delete-orphan")
    responsables = relationship("Responsable", back_populates="proyecto")
