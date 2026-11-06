import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class AlertaSistema(Base):
    """
    Modelo de persistencia para alertas automáticas del sistema generadas por
    la Curva de Espacios Iguales (Scheduler periódico), Perceptrón o VACAS.
    """
    __tablename__ = "alertas_sistema"

    id = Column(String(36), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}")
    proyecto_id = Column(String(36), ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True)
    reunion_id = Column(String(36), ForeignKey("reuniones.id", ondelete="SET NULL"), nullable=True)
    acuerdo_id = Column(String(36), ForeignKey("acuerdos.id", ondelete="SET NULL"), nullable=True)
    
    # ATRASO, OMISION, SLA_EXCEDIDO, VACA_FAILOVER, DATA_DRIFT
    tipo_alerta = Column(String(50), nullable=False)
    # INFO, WARNING, CRITICAL
    nivel_severidad = Column(String(20), default="WARNING", nullable=False)
    
    titulo = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False, nullable=False)
    webhook_enviado = Column(Boolean, default=False, nullable=False)
    
    creada_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizada_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    proyecto = relationship("Proyecto", lazy="joined")
    reunion = relationship("Reunion", lazy="joined")
    acuerdo = relationship("Acuerdo", lazy="joined")

