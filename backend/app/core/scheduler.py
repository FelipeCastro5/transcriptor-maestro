import os
from datetime import datetime
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import SessionLocal
from app.services.reunion_service import reunion_service
from app.services.alert_service import alert_service

class SystemScheduler:
    """
    Gestor de la Curva de Control de Espacios Iguales (Scheduler Autónomo):
    Ejecuta revisiones periódicas sobre la base de datos para detectar compromisos
    vencidos, omisiones de acuerdos en reuniones sucesivas y emitir alertas.
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        # Intervalo en minutos: por defecto 10 minutos para demostraciones en vivo
        self.intervalo_minutos = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "10"))
        self._inicializado = False

    def _tarea_barrido(self):
        """Función ejecutada periódicamente por el scheduler."""
        print(f"[SCHEDULER-TICK] Ejecutando barrido automático de Curva de Espacios Iguales a las {datetime.utcnow().isoformat()}...")
        db = SessionLocal()
        try:
            reunion_service.ejecutar_barrido_acuerdos_periodico(db_session=db)
        except Exception as e:
            print(f"[SCHEDULER-ERROR] Excepción en barrido programado: {e}")
        finally:
            db.close()

    def start(self):
        """Inicia el scheduler en segundo plano si no está activo."""
        if not self._inicializado:
            self.scheduler.add_job(
                func=self._tarea_barrido,
                trigger=IntervalTrigger(minutes=self.intervalo_minutos),
                id="barrido_espacios_iguales",
                name="Curva de Espacios Iguales - Detección de Atrasos y Omisiones",
                replace_existing=True
            )
            self.scheduler.start()
            self._inicializado = True
            print(f"[SCHEDULER] Iniciado exitosamente. Intervalo de ejecución: cada {self.intervalo_minutos} minutos.")

    def shutdown(self):
        """Detiene el scheduler de forma ordenada."""
        if self._inicializado and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self._inicializado = False
            print("[SCHEDULER] Detenido correctamente.")

    def ejecutar_inmediato(self) -> Dict[str, Any]:
        """Permite forzar la ejecución manual del barrido para demostraciones en vivo."""
        db = SessionLocal()
        try:
            return reunion_service.ejecutar_barrido_acuerdos_periodico(db_session=db)
        finally:
            db.close()

    def get_info(self) -> Dict[str, Any]:
        """Retorna el estado de salud y la próxima ejecución del scheduler."""
        proxima = None
        if self._inicializado and self.scheduler.running:
            job = self.scheduler.get_job("barrido_espacios_iguales")
            if job and job.next_run_time:
                proxima = job.next_run_time

        db = SessionLocal()
        try:
            total_alertas = alert_service.contar_no_leidas(db)
        finally:
            db.close()

        return {
            "activo": self.scheduler.running if self._inicializado else False,
            "proxima_ejecucion": proxima,
            "intervalo_minutos": self.intervalo_minutos,
            "total_alertas_activas": total_alertas,
            "modo": "DEMOSTRACION_CONTINUA_ESPACIOS_IGUALES"
        }

system_scheduler = SystemScheduler()

