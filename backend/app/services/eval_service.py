import re
import unicodedata
from typing import List, Dict, Any, Tuple, Set, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.evaluacion import EvaluacionCalibracion
from app.db.models.reunion import Reunion

class EvalService:
    """
    Servicio MLOps de Calibración de Transcripción (WER / WER_w) y Detección de Data Drift.
    Implementa la formulación matemática estricta definida en las métricas del proyecto:
      - Alineación Levenshtein a nivel de palabra
      - Conteo de Sustituciones (S), Eliminaciones (D), Inserciones (I) y Aciertos (H)
      - WER clásico: (S + D + I) / N
      - WER ponderado (WER_w) según criticidad de tokens (Fechas=3.0, Nombres=2.0, Negaciones=3.0)
      - Detección de Data Drift mediante análisis léxico Out-Of-Vocabulary (OOV)
    """

    # Vocabulario Base Inicial de Dominio (Software, Gestión de Proyectos y Jerga Colombiana de Reuniones)
    VOCABULARIO_BASE_DEFAULT: Set[str] = {
        # Gestión y Scrum
        "reunion", "sesion", "seguimiento", "proyecto", "sprint", "equipo", "compromiso", "acuerdo",
        "tarea", "actividad", "pendiente", "entrega", "plazo", "fecha", "revision", "informe", "reporte",
        "mockup", "mockups", "diseno", "interfaz", "frontend", "backend", "endpoint", "endpoints",
        "api", "arquitectura", "base", "datos", "postgres", "fastapi", "angular", "node", "whisper",
        "deepseek", "openai", "perceptron", "vacas", "modelo", "asr", "llm", "transcripcion",
        # Personas y Roles
        "juan", "perez", "maria", "gomez", "carlos", "andres", "camila", "laura", "bryan", "felipe",
        "pedro", "sofia", "responsable", "lider", "desarrollador", "arquitecto",
        # Verbos de Acción
        "entregar", "revisar", "hacer", "terminar", "avanzar", "desarrollar", "implementar", "disenar",
        "probar", "verificar", "validar", "pactar", "acordar", "encargar", "subir", "ajustar",
        # Tiempo y Fechas
        "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo", "hoy", "manana",
        "ayer", "semana", "mes", "octubre", "noviembre", "diciembre", "enero", "febrero", "marzo",
        # Términos Informales y Modismos Colombianos Monitoreados
        "camello", "vuelta", "parche", "pilas", "fresco", "hacerle", "cuadrar", "pillar", "tenaz"
    }

    # Diccionario de Ponderación según la formulación de metricas.md
    PESOS_ARTICULOS_MULETILLAS = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en",
        "por", "con", "y", "o", "u", "e", "eh", "um", "este", "bueno", "oigan", "pues", "si"
    }

    PESOS_NEGACIONES = {
        "no", "nunca", "jamas", "sin", "tampoco", "nada", "nadie"
    }

    PESOS_FECHAS_NUMEROS = {
        "lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo",
        "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre", "diciembre", "hoy", "manana", "ayer",
        "semana", "sprint", "quincena", "primer", "primero", "segundo", "tercero"
    }

    PESOS_NOMBRES_PROPIOS = {
        "juan", "maria", "carlos", "andres", "camila", "laura", "bryan", "felipe",
        "pedro", "sofia", "luis", "ana", "diego", "paola", "mateo", "valentina"
    }

    PESOS_SUSTANTIVOS_VERBOS_CLAVE = {
        "entregar", "revisar", "hacer", "desarrollar", "implementar", "disenar", "probar",
        "informe", "reporte", "mockup", "mockups", "backend", "frontend", "api", "endpoint",
        "endpoints", "arquitectura", "reunion", "compromiso", "acuerdo", "tarea", "pendiente",
        "metrica", "modelo", "whisper", "deepseek", "perceptron", "vacas", "calidad", "despliegue"
    }

    def normalizar_texto(self, texto: str) -> str:
        """Normaliza el texto removiendo signos de puntuación y tildes para comparación objetiva."""
        if not texto:
            return ""
        # Minúsculas
        texto = texto.lower()
        # Normalizar tildes (descomposición canónica)
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
        # Reemplazar puntuación por espacios
        texto = re.sub(r'[^a-z0-9\s%]', ' ', texto)
        # Colapsar espacios múltiples
        return re.sub(r'\s+', ' ', texto).strip()

    def tokenizar(self, texto: str) -> List[str]:
        """Divide el texto normalizado en una lista de palabras."""
        norm = self.normalizar_texto(texto)
        return norm.split() if norm else []

    def obtener_peso_token(self, token: str) -> float:
        """
        Asigna el peso de criticidad según la tabla de metricas.md:
          - Fechas, números y negaciones: 3.0
          - Nombres propios: 2.0
          - Verbos de acción / sustantivos clave: 1.5
          - Artículos, preposiciones y muletillas: 0.3
          - Palabras comunes: 1.0
        """
        if token in self.PESOS_NEGACIONES or token in self.PESOS_FECHAS_NUMEROS or re.match(r'^\d+(?:[.,]\d+)?%?$', token):
            return 3.0
        if token in self.PESOS_NOMBRES_PROPIOS:
            return 2.0
        if token in self.PESOS_SUSTANTIVOS_VERBOS_CLAVE:
            return 1.5
        if token in self.PESOS_ARTICULOS_MULETILLAS:
            return 0.3
        return 1.0

    def alinear_levenshtein(self, ref_tokens: List[str], hyp_tokens: List[str]) -> Tuple[List[Dict[str, Any]], int, int, int, int]:
        """
        Alineación exacta palabra por palabra mediante el algoritmo de Wagner-Fischer (Programación Dinámica).
        Retorna la traza de alineación completa y los totales (S, D, I, H).
        """
        n = len(ref_tokens)
        m = len(hyp_tokens)

        # Matriz de costos dp[i][j]
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        op_matrix = [[""] * (m + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            dp[i][0] = i
            op_matrix[i][0] = "DELETION"

        for j in range(1, m + 1):
            dp[0][j] = j
            op_matrix[0][j] = "INSERTION"

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                    op_matrix[i][j] = "MATCH"
                else:
                    cost_sub = dp[i - 1][j - 1] + 1
                    cost_del = dp[i - 1][j] + 1
                    cost_ins = dp[i][j - 1] + 1

                    min_cost = min(cost_sub, cost_del, cost_ins)
                    dp[i][j] = min_cost

                    if min_cost == cost_sub:
                        op_matrix[i][j] = "SUBSTITUTION"
                    elif min_cost == cost_del:
                        op_matrix[i][j] = "DELETION"
                    else:
                        op_matrix[i][j] = "INSERTION"

        # Backtracking para reconstruir la secuencia de alineación
        i, j = n, m
        alineacion_invertida = []
        s = d = ins = h = 0

        while i > 0 or j > 0:
            op = op_matrix[i][j]
            if op == "MATCH":
                token_ref = ref_tokens[i - 1]
                token_hyp = hyp_tokens[j - 1]
                peso = self.obtener_peso_token(token_ref)
                alineacion_invertida.append({"ref": token_ref, "hyp": token_hyp, "op": "MATCH", "peso": peso})
                h += 1
                i -= 1
                j -= 1
            elif op == "SUBSTITUTION":
                token_ref = ref_tokens[i - 1]
                token_hyp = hyp_tokens[j - 1]
                peso = max(self.obtener_peso_token(token_ref), self.obtener_peso_token(token_hyp))
                alineacion_invertida.append({"ref": token_ref, "hyp": token_hyp, "op": "SUBSTITUTION", "peso": peso})
                s += 1
                i -= 1
                j -= 1
            elif op == "DELETION":
                token_ref = ref_tokens[i - 1]
                peso = self.obtener_peso_token(token_ref)
                alineacion_invertida.append({"ref": token_ref, "hyp": None, "op": "DELETION", "peso": peso})
                d += 1
                i -= 1
            elif op == "INSERTION":
                token_hyp = hyp_tokens[j - 1]
                peso = self.obtener_peso_token(token_hyp)
                alineacion_invertida.append({"ref": None, "hyp": token_hyp, "op": "INSERTION", "peso": peso})
                ins += 1
                j -= 1
            else:
                break

        alineacion = list(reversed(alineacion_invertida))
        return alineacion, s, d, ins, h

    def calcular_wer(
        self,
        texto_referencia: str,
        texto_hipotesis: str,
        modelo_evaluado: str = "whisper-medium",
        reunion_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calcula las métricas de transcripción completas (WER, WER_w, Precisión, Longitud Relativa)
        y persiste el resultado en evaluaciones_calibracion.
        """
        ref_tokens = self.tokenizar(texto_referencia)
        hyp_tokens = self.tokenizar(texto_hipotesis)

        n = len(ref_tokens)
        m = len(hyp_tokens)

        if n == 0:
            raise ValueError("El texto de referencia (Ground Truth) no puede estar vacío.")

        alineacion, s, d, ins, h = self.alinear_levenshtein(ref_tokens, hyp_tokens)

        # 1. WER Clásico
        wer = (s + d + ins) / n

        # 2. WER Ponderado (WER_w)
        # Suma de pesos de errores ponderados
        peso_errores = sum(item["peso"] for item in alineacion if item["op"] in ("SUBSTITUTION", "DELETION", "INSERTION"))
        peso_total_ref = sum(self.obtener_peso_token(t) for t in ref_tokens)
        wer_ponderado = (peso_errores / peso_total_ref) if peso_total_ref > 0 else wer

        # 3. Precisión a nivel de palabra
        precision = h / n

        # 4. Longitud Relativa
        longitud_relativa = m / n

        # 5. Estado de Calidad (Meta: WER < 10% según promesas de entrega)
        if wer <= 0.10:
            estado_calidad = "OPTIMO"
        elif wer < 0.25:
            estado_calidad = "ACEPTABLE"
        else:
            estado_calidad = "CRITICO"

        resultado = {
            "reunion_id": reunion_id,
            "modelo_evaluado": modelo_evaluado,
            "total_palabras_gt": n,
            "total_palabras_hyp": m,
            "sustituciones": s,
            "eliminaciones": d,
            "inserciones": ins,
            "aciertos": h,
            "wer": round(wer, 4),
            "wer_porcentaje": round(wer * 100, 2),
            "wer_ponderado": round(wer_ponderado, 4),
            "wer_ponderado_porcentaje": round(wer_ponderado * 100, 2),
            "precision_palabra": round(precision, 4),
            "precision_palabra_porcentaje": round(precision * 100, 2),
            "longitud_relativa": round(longitud_relativa, 3),
            "estado_calidad": estado_calidad,
            "cumple_meta_sprint": bool(wer <= 0.10),
            "alineacion": alineacion,
            "creado_en": datetime.utcnow()
        }

        # Persistir en BD si la sesión está disponible
        if db:
            registro = EvaluacionCalibracion(
                reunion_id=reunion_id,
                modelo_evaluado=modelo_evaluado,
                total_palabras_gt=n,
                total_palabras_hyp=m,
                sustituciones=s,
                eliminaciones=d,
                inserciones=ins,
                aciertos=h,
                wer=resultado["wer"],
                wer_ponderado=resultado["wer_ponderado"],
                precision_palabra=resultado["precision_palabra"],
                longitud_relativa=resultado["longitud_relativa"],
                estado_calidad=estado_calidad,
                detalles_alineacion=alineacion[:50]  # Muestra inicial para evitar sobrecarga JSON
            )
            db.add(registro)
            db.commit()
            db.refresh(registro)
            resultado["id"] = registro.id
        else:
            resultado["id"] = "CALIB-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")

        return resultado

    def analizar_data_drift(
        self,
        texto: str,
        vocabulario_adicional: Optional[List[str]] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Detecta Data Drift comparando las palabras del texto actual contra el vocabulario base de referencia.
        Calcula el ratio Out-Of-Vocabulary (OOV) y alerta sobre términos coloquiales o de jerga no catalogados.
        """
        vocab_base = set(self.VOCABULARIO_BASE_DEFAULT)

        # Si hay vocabulario adicional provisto por el usuario
        if vocabulario_adicional:
            for w in vocabulario_adicional:
                vocab_base.add(self.normalizar_texto(w))

        # Enriquecer con transcripciones previas si la BD está presente
        if db:
            reuniones_previas = db.query(Reunion.transcripcion_texto).filter(Reunion.transcripcion_texto.isnot(None)).limit(10).all()
            for r in reuniones_previas:
                if r[0]:
                    tokens = self.tokenizar(r[0])
                    vocab_base.update(tokens)

        tokens_texto = self.tokenizar(texto)
        if not tokens_texto:
            return {
                "total_palabras_evaluadas": 0,
                "palabras_unicas_evaluadas": 0,
                "tamano_vocabulario_base": len(vocab_base),
                "palabras_oov_detectadas": [],
                "total_palabras_oov": 0,
                "ratio_oov": 0.0,
                "ratio_oov_porcentaje": 0.0,
                "estado_drift": "ESTABLE",
                "alerta_drift": False,
                "recomendacion": "El texto evaluado está vacío."
            }

        palabras_unicas = set(tokens_texto)
        # Palabras fuera del vocabulario (OOV)
        oov_words = [w for w in palabras_unicas if w not in vocab_base and not re.match(r'^\d+$', w)]

        ratio_oov = len(oov_words) / len(palabras_unicas)

        # Umbrales de evaluación de drift
        if ratio_oov < 0.15:
            estado_drift = "ESTABLE"
            alerta_drift = False
            recomendacion = "El vocabulario está alineado con el dominio corporativo esperado. Sin indicios de drift."
        elif ratio_oov < 0.30:
            estado_drift = "MODERADO"
            alerta_drift = True
            recomendacion = "Se detectó divergencia léxica moderada. Se sugiere verificar modismos o terminología técnica no indexada."
        else:
            estado_drift = "CRITICO_DRIFT"
            alerta_drift = True
            recomendacion = "Alto Data Drift detectado (>30% OOV). Posible cambio radical de dialecto o jerga informal no contemplada."

        return {
            "total_palabras_evaluadas": len(tokens_texto),
            "palabras_unicas_evaluadas": len(palabras_unicas),
            "tamano_vocabulario_base": len(vocab_base),
            "palabras_oov_detectadas": sorted(oov_words)[:30],  # Primeras 30 para visualización concisa
            "total_palabras_oov": len(oov_words),
            "ratio_oov": round(ratio_oov, 4),
            "ratio_oov_porcentaje": round(ratio_oov * 100, 2),
            "estado_drift": estado_drift,
            "alerta_drift": alerta_drift,
            "recomendacion": recomendacion
        }

eval_service = EvalService()
