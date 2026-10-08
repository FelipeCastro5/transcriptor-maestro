import time
import json
from typing import Optional, Tuple, Dict, Any, List
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.perceptron import perceptron, NivelError, EstadoBinario

class VACASManager:
    """
    Sistema de Respaldo Gemelo (VACAS):
    Garantiza la alta disponibilidad y tolerancia a fallos de los LLMs.
    Si el proveedor primario falla por timeout (>3s), HTTP 5xx o no está configurado,
    conmuta automáticamente en caliente (< 1.5s) al proveedor réplica o al motor local.
    """

    PROVEEDOR_PRIMARIO = "DEEPSEEK_API"
    PROVEEDOR_REPLICA = "OPENAI_REPLICA"
    PROVEEDOR_EMERGENCIA = "OFFLINE_RULES"

    def __init__(self):
        self.simular_fallo_primaria: bool = False  # Modo de prueba (Chaos Testing)

    def _llamar_deepseek(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Llamada a la VACA Primaria (DeepSeek)."""
        if self.simular_fallo_primaria:
            print("[VACAS] SIMULACIÓN DE FALLO: Forzando caída de VACA Primaria (DeepSeek).")
            raise ConnectionError("Fallo simulado por Chaos Engineering (HTTP 500)")

        api_key = settings.DEEPSEEK_API_KEY
        if not api_key or api_key.startswith("tu-"):
            # Sin API Key real, se considera fallo inmediato para activar contingencia
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }

        with httpx.Client(timeout=3.0) as client:
            res = client.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            raise httpx.HTTPStatusError(f"HTTP {res.status_code}", request=res.request, response=res)

    def _llamar_replica_secundaria(self, prompt: str, system_prompt: str) -> Optional[str]:
        """Llamada a la VACA Réplica (OpenAI / Proveedor secundario si configurado)."""
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        with httpx.Client(timeout=3.0) as client:
            res = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"].strip()
            return None

    def ejecutar_con_conmutacion(
        self,
        prompt: str,
        system_prompt: str,
        reunion_id: str,
        etapa: str,
        db: Optional[Session] = None
    ) -> Tuple[Optional[str], str, bool, int]:
        """
        Ejecuta la inferencia aplicando el conmutador de contingencia.
        Retorna: (resultado_texto, proveedor_usado, conmutacion_ocurrida, latencia_ms)
        """
        inicio = time.time()
        conmutacion_ocurrida = False
        resultado = None
        proveedor_final = self.PROVEEDOR_PRIMARIO
        fallo_detectado = False

        # 1. Intentar con VACA Primaria
        try:
            resultado = self._llamar_deepseek(prompt, system_prompt)
            if resultado is None:
                fallo_detectado = True
        except Exception as e:
            print(f"[VACAS] Fallo en VACA Primaria ({e}). Disparando conmutación en caliente...")
            fallo_detectado = True

        # 2. Conmutación a VACA Réplica si la primaria falló
        if fallo_detectado or resultado is None:
            conmutacion_ocurrida = True
            try:
                resultado = self._llamar_replica_secundaria(prompt, system_prompt)
                if resultado:
                    proveedor_final = self.PROVEEDOR_REPLICA
                else:
                    proveedor_final = self.PROVEEDOR_EMERGENCIA
            except Exception as e:
                print(f"[VACAS] Fallo en Réplica secundaria ({e}). Activando VACA de Emergencia...")
                proveedor_final = self.PROVEEDOR_EMERGENCIA

        latencia_ms = int((time.time() - inicio) * 1000)

        # 3. Clasificación y Auditoría con El Perceptrón
        estado_binario, nivel_error = perceptron.clasificar_ejecucion(
            latencia_ms=latencia_ms,
            fallo_proveedor=fallo_detectado,
            conmutacion_activada=conmutacion_ocurrida
        )

        if db and reunion_id:
            try:
                perceptron.registrar_log(
                    db=db,
                    reunion_id=reunion_id,
                    etapa=etapa,
                    proveedor=proveedor_final,
                    latencia_ms=latencia_ms,
                    estado_binario=estado_binario,
                    nivel_error=nivel_error,
                    conmutacion_vaca=conmutacion_ocurrida
                )
            except Exception as e:
                print(f"[VACAS] No se pudo guardar telemetría en DB: {e}")

        print(f"[VACAS] Ejecución finalizada: Proveedor={proveedor_final}, Conmutación={conmutacion_ocurrida}, Latencia={latencia_ms}ms, Estado={estado_binario}")
        return resultado, proveedor_final, conmutacion_ocurrida, latencia_ms

vacas_manager = VACASManager()
