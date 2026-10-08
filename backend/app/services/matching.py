import re
from typing import List, Tuple, Optional, Dict, Any

class FuzzyMatcher:
    """
    Inteligencia 2: Motor Lógico de Emparejamiento con Tolerancia al Error (Fuzzy Matching).
    Implementa la distancia de Levenshtein y normalización de entidades para mitigar
    errores de transcripción fonética y tipográfica en nombres propios y acuerdos.
    """

    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """Limpia caracteres especiales, tildes y espacios redundantes."""
        if not texto:
            return ""
        texto = texto.lower().strip()
        reemplazos = (
            ("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"),
            ("ñ", "n"), ("ü", "u")
        )
        for origen, destino in reemplazos:
            texto = texto.replace(origen, destino)
        return re.sub(r'[^a-z0-9\s]', '', texto)

    @classmethod
    def distancia_levenshtein(cls, s1: str, s2: str) -> int:
        """
        Calcula el número mínimo de operaciones (inserciones, eliminaciones, sustituciones)
        para transformar s1 en s2.
        """
        s1 = cls.normalizar_texto(s1)
        s2 = cls.normalizar_texto(s2)

        if len(s1) < len(s2):
            return cls.distancia_levenshtein(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def similitud_ratio(cls, s1: str, s2: str) -> float:
        """
        Calcula un ratio de similitud normalizado entre 0.0 (totalmente diferente) y 1.0 (idéntico).
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        n1 = cls.normalizar_texto(s1)
        n2 = cls.normalizar_texto(s2)

        # Si uno es subconjunto de otro (ej: "Juan" en "Juan Pérez")
        if n1 in n2 or n2 in n1:
            return 0.95

        dist = cls.distancia_levenshtein(n1, n2)
        max_len = max(len(n1), len(n2))
        if max_len == 0:
            return 1.0
        return round(1.0 - (dist / max_len), 3)

    @classmethod
    def emparejar_responsable(
        cls,
        nombre_crudo: str,
        catalogo_responsables: list,
        umbral: float = 0.70
    ) -> Tuple[Optional[Any], str, float]:
        """
        Empareja un nombre extraído por Whisper/LLM contra el catálogo oficial de responsables.
        Retorna: (objeto_responsable_db, nombre_oficial_resuelto, score_similitud)
        """
        if not nombre_crudo or nombre_crudo.lower() in ["no asignado", "no especificado", "por definir"]:
            return None, nombre_crudo or "No asignado", 1.0

        mejor_candidato = None
        mejor_score = 0.0
        nombre_resuelto = nombre_crudo

        for resp in catalogo_responsables:
            nombre_oficial = resp.nombre_completo
            # 1. Comparar con nombre completo
            score_oficial = cls.similitud_ratio(nombre_crudo, nombre_oficial)
            if score_oficial > mejor_score:
                mejor_score = score_oficial
                mejor_candidato = resp
                nombre_resuelto = nombre_oficial

            # 2. Comparar con lista de alias conocidos
            alias_lista = resp.alias_conocidos if isinstance(resp.alias_conocidos, list) else []
            for alias in alias_lista:
                score_alias = cls.similitud_ratio(nombre_crudo, str(alias))
                if score_alias > mejor_score:
                    mejor_score = score_alias
                    mejor_candidato = resp
                    nombre_resuelto = nombre_oficial

        # Si supera el umbral de tolerancia
        if mejor_score >= umbral and mejor_candidato:
            return mejor_candidato, nombre_resuelto, mejor_score

        # Si no alcanza el umbral, se preserva el texto crudo para revisión
        return None, nombre_crudo, mejor_score

    @classmethod
    def detectar_cumplimiento_historico(
        cls,
        transcripcion: str,
        acuerdos_pendientes: list
    ) -> List[Dict[str, Any]]:
        """
        Pilar 3: Cruza la transcripción actual contra acuerdos pendientes de reuniones pasadas
        para detectar si se dio por terminada alguna tarea previa.
        """
        texto_norm = cls.normalizar_texto(transcripcion)
        patrones_cumplimiento = [
            r"ya (?:quedo|esta|entregue|hice|subi|termine|cerre|envie)",
            r"(?:quedo|esta) listo",
            r"complet(?:e|amos|ado)",
            r"se cerro la tarea"
        ]

        acuerdos_detectados = []
        for acuerdo in acuerdos_pendientes:
            tarea_norm = cls.normalizar_texto(acuerdo.tarea_desc)
            palabras_clave = [p for p in tarea_norm.split() if len(p) > 3]

            # Buscar si se menciona la tarea en contexto de haber sido terminada
            coincidencias = sum(1 for p in palabras_clave if p in texto_norm)
            ratio_coincidencia = coincidencias / len(palabras_clave) if palabras_clave else 0

            # Si se mencionan la mayoría de palabras de la tarea y hay patrones de cierre
            if ratio_coincidencia >= 0.6:
                for patron in patrones_cumplimiento:
                    if re.search(patron, texto_norm):
                        acuerdos_detectados.append({
                            "acuerdo_id": acuerdo.id,
                            "tarea_desc": acuerdo.tarea_desc,
                            "estado_nuevo": "completado",
                            "motivo": f"Detectado cumplimiento en conversación de la reunión actual (coincidencia {int(ratio_coincidencia*100)}%)"
                        })
                        break

        return acuerdos_detectados

fuzzy_matcher = FuzzyMatcher()
