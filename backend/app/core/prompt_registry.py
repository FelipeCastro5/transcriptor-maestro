import hashlib
from typing import List, Dict, Any, Optional

class PromptVersion:
    def __init__(
        self,
        id: str,
        version: str,
        nombre: str,
        descripcion: str,
        prompt_sistema: str,
        template_usuario: str,
        modelos_compatibles: List[str],
        es_activo: bool = False,
        creado_en: str = "2026-10-15T00:00:00Z"
    ):
        self.id = id
        self.version = version
        self.nombre = nombre
        self.descripcion = descripcion
        self.prompt_sistema = prompt_sistema
        self.template_usuario = template_usuario
        self.modelos_compatibles = modelos_compatibles
        self.es_activo = es_activo
        self.creado_en = creado_en
        self.hash_md5 = self._calcular_hash()

    def _calcular_hash(self) -> str:
        contenido = f"{self.prompt_sistema}|{self.template_usuario}"
        return hashlib.md5(contenido.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "hash_md5": self.hash_md5,
            "modelos_compatibles": self.modelos_compatibles,
            "es_activo": self.es_activo,
            "prompt_sistema": self.prompt_sistema,
            "creado_en": self.creado_en
        }

class PromptRegistry:
    """
    Registro y Versionador de Prompts y Modelos (Prompt Registry MLOps).
    Permite auditar el hash, controlar versiones activas y realizar despliegue de prompts en caliente.
    """

    def __init__(self):
        self._prompts: Dict[str, PromptVersion] = {}
        self._inicializar_versiones()

    def _inicializar_versiones(self):
        # Versión 1: Base Formal
        p1 = PromptVersion(
            id="PRM-V1-BASE",
            version="1.0.0",
            nombre="Prompt Base Formal (Sprint 1)",
            descripcion="Extracción estándar de compromisos directos orientada a reuniones ejecutivas estructuradas.",
            prompt_sistema="Eres un asistente corporativo de gestión de proyectos que extrae acuerdos en formato JSON estricto.",
            template_usuario="""Analiza la siguiente transcripción y extrae todos los acuerdos, tareas y compromisos:

TRANSCRIPCIÓN:
{texto}

Responde SOLO con una lista JSON de objetos con los campos:
- tarea_desc: qué hay que hacer
- responsable: quién debe hacerlo
- fecha_compromiso: fecha o null
- fragmento_original: frase exacta donde se pactó""",
            modelos_compatibles=["deepseek-chat", "gpt-4o-mini", "rules-offline"],
            es_activo=False,
            creado_en="2026-08-20T10:00:00Z"
        )

        # Versión 2: Informal con Modismos Colombianos
        p2 = PromptVersion(
            id="PRM-V2-INFORMAL",
            version="2.1.0",
            nombre="Prompt Especializado en Jerga Informal y Coloquialismos",
            descripcion="Optimizado para audio no estructurado con modismos colombianos ('hacer la vuelta', 'camello', 'pilas', 'parche').",
            prompt_sistema="Eres un asistente experto en lingüística computacional y dialecto colombiano para extracción de compromisos.",
            template_usuario="""Eres un asistente especializado en extraer ACUERDOS, DECISIONES y COMPROMISOS de conversaciones informales.
Analiza la siguiente transcripción e interpreta modismos como "hacer la vuelta" (realizar trámite/tarea) o "yo le jalo" (asumo compromiso).
Extrae TODOS los momentos donde:
1. Alguien asigna una tarea a alguien.
2. Alguien se compromete a hacer algo ("yo me encargo", "lo haré", "pilas con eso").
3. Se toma una decisión o se acuerda una entrega.

Para cada acuerdo extrae:
- tarea_desc: descripción concisa y clara de la tarea
- responsable: persona responsable (infiere por el contexto)
- fecha_compromiso: fecha o plazo límite si se menciona, de lo contrario null
- fragmento_original: la cita textual exacta del audio

TRANSCRIPCIÓN:
{texto}

Responde ÚNICAMENTE con un JSON válido que sea una lista de objetos:
[
  {{"tarea_desc": "...", "responsable": "...", "fecha_compromiso": "...", "fragmento_original": "..."}}
]""",
            modelos_compatibles=["deepseek-chat", "gpt-4o-mini"],
            es_activo=True,  # Activo por defecto según la estrategia 4/5
            creado_en="2026-09-15T14:30:00Z"
        )

        # Versión 3: Híbrido Maduro con Jerarquía y Verificación Cruzada
        p3 = PromptVersion(
            id="PRM-V3-HIBRIDO",
            version="3.0.0",
            nombre="Prompt Híbrido Maduro Multi-Dominio (Sprint 3 / VACAS)",
            descripcion="Modelo avanzado con inferencia de compromisos implícitos, detección de bloqueantes y dependencias entre responsables.",
            prompt_sistema="Eres un motor cognitivo de seguimiento de acuerdos de alta fidelidad con verificación cruzada.",
            template_usuario="""Analiza rigurosamente la transcripción suministrada identificando compromisos explícitos e implícitos.
Mapea dependencias entre tareas y asigna fechas normalizadas.
Si hay ambigüedad en el responsable, asigna al líder de área o marca como 'Equipo General'.

TRANSCRIPCIÓN:
{texto}

Estructura de salida JSON requerida:
[
  {{
    "tarea_desc": "descripción de la tarea",
    "responsable": "nombre del responsable",
    "fecha_compromiso": "fecha estimada o null",
    "fragmento_original": "evidencia textual exacta"
  }}
]""",
            modelos_compatibles=["deepseek-chat", "gpt-4o-mini"],
            es_activo=False,
            creado_en="2026-10-28T09:00:00Z"
        )

        self._prompts[p1.id] = p1
        self._prompts[p2.id] = p2
        self._prompts[p3.id] = p3

    def listar_prompts(self) -> List[Dict[str, Any]]:
        """Retorna el catálogo completo de versiones registradas."""
        return [p.to_dict() for p in self._prompts.values()]

    def obtener_prompt_activo(self) -> PromptVersion:
        """Retorna la versión activa de prompt actual."""
        for p in self._prompts.values():
            if p.es_activo:
                return p
        # Fallback al primero
        return list(self._prompts.values())[0]

    def obtener_prompt_por_id(self, prompt_id: str) -> Optional[PromptVersion]:
        """Busca un prompt por su identificador único."""
        return self._prompts.get(prompt_id)

    def activar_version(self, prompt_id: str) -> bool:
        """Activa una versión específica de prompt en caliente."""
        if prompt_id not in self._prompts:
            return False
        for pid, p in self._prompts.items():
            p.es_activo = (pid == prompt_id)
        return True

prompt_registry = PromptRegistry()

