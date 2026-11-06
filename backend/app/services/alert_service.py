import os
import uuid
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models.alerta import AlertaSistema
from app.core.config import settings

class AlertService:
    """
    Servicio de gestión y emisión de alertas del sistema.
    Permite notificar al usuario sobre tareas atrasadas, omisiones y fallos,
    cumpliendo con la Inteligencia Interpersonal y la Curva de Espacios Iguales.
    """

    WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")  # URL opcional (Discord / Slack / Webhook.site)

    @classmethod
    def emitir_alerta(
        cls,
        db: Session,
        tipo_alerta: str,
        titulo: str,
        mensaje: str,
        nivel_severidad: str = "WARNING",
        proyecto_id: Optional[str] = None,
        reunion_id: Optional[str] = None,
        acuerdo_id: Optional[str] = None,
        disparar_webhook: bool = True
    ) -> AlertaSistema:
        """
        Crea una nueva alerta en base de datos y despacha la notificación.
        """
        alerta_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        nueva_alerta = AlertaSistema(
            id=alerta_id,
            proyecto_id=proyecto_id,
            reunion_id=reunion_id,
            acuerdo_id=acuerdo_id,
            tipo_alerta=tipo_alerta,
            nivel_severidad=nivel_severidad,
            titulo=titulo,
            mensaje=mensaje,
            leida=False,
            webhook_enviado=False,
            creada_en=datetime.utcnow(),
            actualizada_en=datetime.utcnow()
        )

        db.add(nueva_alerta)
        db.commit()
        db.refresh(nueva_alerta)

        if disparar_webhook:
            webhook_ok = cls._despachar_webhook(nueva_alerta)
            if webhook_ok:
                nueva_alerta.webhook_enviado = True
                db.commit()

        print(f"[ALERTA-{nivel_severidad}] {tipo_alerta}: {titulo} (ID: {alerta_id})")
        return nueva_alerta

    @classmethod
    def _despachar_webhook(cls, alerta: AlertaSistema) -> bool:
        """
        Despacha un payload JSON hacia el webhook externo configurado o genera
        el log simulado de notificación empresarial para sustentación local.
        """
        payload = {
            "evento": "SISTEMA_TRANSCRIPTOR_ALERTA",
            "alerta_id": alerta.id,
            "tipo": alerta.tipo_alerta,
            "severidad": alerta.nivel_severidad,
            "titulo": alerta.titulo,
            "mensaje": alerta.mensaje,
            "acuerdo_id": alerta.acuerdo_id,
            "reunion_id": alerta.reunion_id,
            "timestamp": alerta.creada_en.isoformat()
        }

        # Si hay un Webhook real configurado (ej: Discord / Slack)
        if cls.WEBHOOK_URL and cls.WEBHOOK_URL.startswith("http"):
            try:
                # Formatear amigable para Discord/Slack si aplica
                formato_discord = {
                    "content": f"⚠️ **[{alerta.nivel_severidad}] {alerta.titulo}**\n{alerta.mensaje}\n*Alerta ID: {alerta.id}*"
                }
                with httpx.Client(timeout=3.0) as client:
                    resp = client.post(cls.WEBHOOK_URL, json=formato_discord)
                    return resp.status_code in [200, 204]
            except Exception as e:
                print(f"[WEBHOOK-ERROR] No se pudo despachar webhook externo: {e}")
                return False

        # En modo local/desarrollo sin webhook externo, se simula el despacho exitoso
        print(f"[SIMULADOR-NOTIFICACION] Despacho exitoso de alerta {alerta.id} a supervisor (Email/Webhook Mock)")
        return True

    @classmethod
    def listar_alertas(
        cls,
        db: Session,
        solo_no_leidas: bool = False,
        limite: int = 50
    ) -> List[AlertaSistema]:
        """
        Retorna las alertas registradas ordenadas cronológicamente de forma descendente.
        """
        query = db.query(AlertaSistema)
        if solo_no_leidas:
            query = query.filter(AlertaSistema.leida == False)
        return query.order_by(desc(AlertaSistema.creada_en)).limit(limite).all()

    @classmethod
    def marcar_como_leida(cls, db: Session, alerta_id: str) -> Optional[AlertaSistema]:
        """
        Marca una alerta específica como atendida/leída.
        """
        alerta = db.query(AlertaSistema).filter(AlertaSistema.id == alerta_id).first()
        if alerta:
            alerta.leida = True
            alerta.actualizada_en = datetime.utcnow()
            db.commit()
            db.refresh(alerta)
        return alerta

    @classmethod
    def contar_no_leidas(cls, db: Session) -> int:
        return db.query(AlertaSistema).filter(AlertaSistema.leida == False).count()

alert_service = AlertService()

