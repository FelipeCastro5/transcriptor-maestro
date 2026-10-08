import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class AuditoriaIALog(Base):
    __tablename__ = "auditoria_ia_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reunion_id = Column(String(36), ForeignKey("reuniones.id", ondelete="CASCADE"), nullable=False)
    etapa = Column(String(50), nullable=False)  # ASR, LLM_EXTRACCION, LLM_RESUMEN
    proveedor = Column(String(50), nullable=False)  # DEEPSEEK, OPENAI, HUGGINGFACE_LOCAL
    estado_binario = Column(Integer, default=0)  # 0=Exito, 1=Fallo
    nivel_error = Column(Integer, default=4)     # Jerarquía 0 a 4
    latencia_ms = Column(Integer, nullable=True)
    conmutacion_vaca = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    reunion = relationship("Reunion", back_populates="auditoria_logs")
