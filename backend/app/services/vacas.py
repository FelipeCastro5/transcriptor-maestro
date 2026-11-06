import time
import json
import concurrent.futures
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

    def _llamar_deepseek(self, prompt: str, system_prompt: str, modelo: str = "deepseek-chat") -> Optional[str]:
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
            "model": modelo,
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

    def _llamar_openai(self, prompt: str, system_prompt: str, modelo: str = "gpt-4o-mini") -> Optional[str]:
        """Llamada a la VACA Réplica (OpenAI / Proveedor secundario si configurado)."""
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return None

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": modelo,
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

    def _calcular_discrepancia(self, texto1: Optional[str], texto2: Optional[str]) -> float:
        """
        Calcula la métrica de discrepancia léxica entre dos respuestas de LLMs.
        Utiliza distancia de edición a nivel de tokens normalizada por longitud máxima.
        """
        if not texto1 and not texto2:
            return 0.0
        if not texto1 or not texto2:
            return 1.0

        t1 = texto1.lower().split()
        t2 = texto2.lower().split()
        n, m = len(t1), len(t2)
        if n == 0 and m == 0:
            return 0.0
        if n == 0 or m == 0:
            return 1.0

        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = i
        for j in range(m + 1):
            dp[0][j] = j

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = 0 if t1[i - 1] == t2[j - 1] else 1
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

        max_len = max(n, m)
        return dp[n][m] / max_len if max_len > 0 else 0.0

    def ejecutar_con_conmutacion(
        self,
        prompt: str,
        system_prompt: str,
        reunion_id: str,
        etapa: str,
        db: Optional[Session] = None,
        llm_preferido: str = "deepseek",
        modelo_llm: str = "deepseek-chat",
        modo_consenso: bool = False
    ) -> Tuple[Optional[str], str, bool, int]:
        """
        Ejecuta la inferencia aplicando conmutación en caliente (VACAS) o Modo Consenso Concurrente.
        Retorna: (resultado_texto, proveedor_usado, conmutacion_ocurrida, latencia_ms)
        """
        inicio = time.time()
        conmutacion_ocurrida = False
        resultado = None

        if llm_preferido.lower() == "openai":
            func_primaria = lambda: self._llamar_openai(prompt, system_prompt, modelo_llm)
            func_secundaria = lambda: self._llamar_deepseek(prompt, system_prompt, "deepseek-chat")
            nombre_primaria = "OPENAI_API"
            nombre_secundaria = "DEEPSEEK_REPLICA"
        else:
            func_primaria = lambda: self._llamar_deepseek(prompt, system_prompt, modelo_llm)
            func_secundaria = lambda: self._llamar_openai(prompt, system_prompt, "gpt-4o-mini")
            nombre_primaria = "DEEPSEEK_API"
            nombre_secundaria = "OPENAI_REPLICA"

        proveedor_final = nombre_primaria
        fallo_detectado = False
        nivel_error_forzado: Optional[int] = None

        # =====================================================================
        # MODO CONSENSO CONCURRENTE DUAL (DeepSeek + OpenAI en paralelo)
        # =====================================================================
        if modo_consenso:
            print(f"[VACAS] MODO CONSENSO DUAL ACTIVADO: Invocando concurrentemente {nombre_primaria} y {nombre_secundaria}...")
            res_primaria = None
            res_secundaria = None

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                f_prim = executor.submit(func_primaria)
                f_sec = executor.submit(func_secundaria)

                try:
                    res_primaria = f_prim.result(timeout=3.5)
                except Exception as e:
                    print(f"[VACAS-CONSENSO] Fallo en primaria: {e}")
                    res_primaria = None

                try:
                    res_secundaria = f_sec.result(timeout=3.5)
                except Exception as e:
                    print(f"[VACAS-CONSENSO] Fallo en réplica: {e}")
                    res_secundaria = None

            # Caso 1: Ambos modelos respondieron exitosamente -> Evaluación de Discrepancia
            if res_primaria and res_secundaria:
                discrepancia = self._calcular_discrepancia(res_primaria, res_secundaria)
                print(f"[VACAS-CONSENSO] Discrepancia calculada entre modelos: {round(discrepancia * 100, 2)}%")

                if discrepancia > 0.20:
                    # Discrepancia > 20%: Alerta Perceptrón Nivel 2
                    nivel_error_forzado = NivelError.NIVEL_2_MEDIO.value
                    proveedor_final = f"CONSENSO_DIVERGENTE ({nombre_primaria} vs {nombre_secundaria}, disc={round(discrepancia*100, 1)}%)"
                    resultado = res_primaria
                else:
                    nivel_error_forzado = NivelError.NIVEL_4_INFORMATIVO.value
                    proveedor_final = f"CONSENSO_DUAL_OK ({nombre_primaria}+{nombre_secundaria}, disc={round(discrepancia*100, 1)}%)"
                    resultado = res_primaria

            # Caso 2: Solo uno de los modelos respondió -> Tolerancia a Fallos sin bloqueo
            elif res_primaria or res_secundaria:
                conmutacion_ocurrida = True
                fallo_detectado = True
                resultado = res_primaria if res_primaria else res_secundaria
                proveedor_final = nombre_primaria if res_primaria else nombre_secundaria
                print(f"[VACAS-CONSENSO] Un proveedor falló, usando sobreviviente: {proveedor_final}")

            # Caso 3: Ambos fallaron -> Contingencia a Reglas Offline
            else:
                conmutacion_ocurrida = True
                fallo_detectado = True
                resultado = None
                proveedor_final = self.PROVEEDOR_EMERGENCIA
                print("[VACAS-CONSENSO] Ambos proveedores fallaron. Redirigiendo a VACA Emergencia.")

        # =====================================================================
        # MODO SECUENCIAL ESTÁNDAR (Conmutación en Caliente < 1.5s)
        # =====================================================================
        else:
            # 1. Intentar con VACA Primaria
            try:
                resultado = func_primaria()
                if resultado is None:
                    fallo_detectado = True
            except Exception as e:
                print(f"[VACAS] Fallo en VACA Primaria ({e}). Disparando conmutacion en caliente...")
                fallo_detectado = True

            # 2. Conmutacion a VACA Replica si la primaria fallo
            if fallo_detectado or resultado is None:
                conmutacion_ocurrida = True
                try:
                    resultado = func_secundaria()
                    if resultado:
                        proveedor_final = nombre_secundaria
                    else:
                        proveedor_final = self.PROVEEDOR_EMERGENCIA
                except Exception as e:
                    print(f"[VACAS] Fallo en Replica secundaria ({e}). Activando VACA de Emergencia...")
                    proveedor_final = self.PROVEEDOR_EMERGENCIA

        latencia_ms = int((time.time() - inicio) * 1000)

        # 3. Clasificación y Auditoría con El Perceptrón
        estado_binario, nivel_error = perceptron.clasificar_ejecucion(
            latencia_ms=latencia_ms,
            fallo_proveedor=fallo_detectado,
            conmutacion_activada=conmutacion_ocurrida
        )

        if nivel_error_forzado is not None:
            nivel_error = nivel_error_forzado

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

        print(f"[VACAS] Inferencia finalizada: Proveedor={proveedor_final}, Conmutación={conmutacion_ocurrida}, Latencia={latencia_ms}ms, Estado={estado_binario}, NivelError={nivel_error}")
        return resultado, proveedor_final, conmutacion_ocurrida, latencia_ms

vacas_manager = VACASManager()
