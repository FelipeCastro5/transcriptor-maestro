# 🎯 Patrón de Oro (Ground Truth): Cuadro de Control y Acuerdos de la Reunión
> **Fuente Oficial de la Verdad:** Transcripción y Acuerdos Verificados de [`new-guion.md`](./new-guion.md)  
> **Propósito:** Servir como patrón de referencia canónico (*Ground Truth*) para evaluar y comparar cuantitativamente el desempeño de los modelos de Inteligencia Artificial (Whisper Small, Whisper Medium y Whisper Large / LLMs de extracción).

---

## 📌 Resumen Ejecutivo de la Reunión

El equipo del proyecto **Transcriptor Maestro** llevó a cabo su sesión semanal de sincronización técnica para definir el cierre de la entrega final. En la primera fase, se validaron los resultados empíricos del benchmarking de modelos ASR, ratificando a **Whisper Medium** como la opción óptima frente a Small (pérdida de términos técnicos) y Large (alta latencia y riesgo de desbordamiento de memoria sin fragmentación). Asimismo, se confirmó la estabilidad de la arquitectura modular en FastAPI con soporte de contingencia VACAS y base de datos relacional.

En la toma de decisiones, se aprobó la implementación de concurrencia real mediante `ThreadPoolExecutor` para el **Modo Consenso Dual** entre DeepSeek y OpenAI con el objetivo de preservar el SLA de latencia por debajo de tres segundos, adoptando en paralelo el **Calibrador de WER Ponderado** (Levenshtein con sobrepeso en fechas, cifras y responsables) y el detector de deriva léxica. Finalmente, se asignaron tres compromisos clave con fechas límites estrictas: integración del panel de Auditoría MLOps en Angular (Alejandro Martínez), endpoint/botón de cancelación de tareas en curso junto con el informe técnico APA 7 (Daniel Felipe Castro), y redacción del guion narrativo articulado con las diapositivas de sustentación (Bryan Betancourt).

---

## 📋 Catálogo de Integrantes y Mapeo de Identidades (Fuzzy Matching)

| Nombre Canónico (BD) | Rol en el Proyecto | Variantes / Apodos Usados en la Reunión |
| :--- | :--- | :--- |
| **Bryan Betancourt** | Scrum Master & Líder de Frontend / UX | Bryan |
| **Daniel Felipe Castro** | Arquitecto de Software & Líder Backend / IA | Felipe |
| **Alejandro Martínez** | Ingeniero de MLOps, Datos y Resiliencia | Alejo |

---

## 📊 Matriz de Compromisos Extraídos (Ground Truth)

| # | Descripción de la Tarea | Responsable Oficial | Alias Detectado | Fecha y Hora de Compromiso | Estado | Fragmento Textual Original (Evidencia / Cita Exacta) |
| :-: | :--- | :--- | :--- | :--- | :-: | :--- |
| **1** | Culminar la integración del panel de Auditoría MLOps en el frontend de Angular (telemetría VACAS con Chaos Testing, calibración WER en vivo, monitor de deriva léxica OOV y Prompt Registry con hash MD5). | **Alejandro Martínez** | Alejo | Jueves 12 de noviembre a las 6:00 pm (18:00) | `pendiente` | *"Yo me encargo de culminar la integración del panel de Auditoría MLOps en el frontend de Angular y me comprometo a tenerlo funcionando y conectado con la API a más tardar este jueves 12 de noviembre a las 6:00 de la tarde."* |
| **2** | Implementar el endpoint y botón de cancelación segura de procesamientos en curso (liberando memoria y purgando temporales), y estructurar el documento formal de entrega en Word y PDF bajo lineamientos APA 7 completos sin emojis. | **Daniel Felipe Castro** | Felipe | Viernes 13 de noviembre a las 2:00 pm (14:00) | `pendiente` | *"Yo me comprometo a implementar el endpoint de cancelación en el backend con su respectivo botón en la interfaz de usuario, y a estructurar el documento formal de entrega en Word y PDF bajo lineamientos APA 7 completos. Entrego ambos entregables probados este viernes 13 de noviembre a las 2:00 de la tarde."* |
| **3** | Articular el guion narrativo de sustentación unificando la evolución histórica de los tres cortes del semestre y construir la presentación ejecutiva de soporte (diapositivas finales). | **Bryan Betancourt** | Bryan | Sábado 14 de noviembre antes de las 11:00 am | `pendiente` | *"Por mi cuenta, yo asumo la responsabilidad de articular el guion narrativo de sustentación unificando la evolución histórica de los tres cortes del semestre y construir la presentación ejecutiva de soporte. Me comprometo a tener listas las diapositivas y el guion definitivo este sábado 14 de noviembre antes de las 11:00 de la mañana."* |

---

## 🔄 Tareas Previas Revisadas (Cierres y Validaciones Históricas)

| Tarea Anterior Revisada | Responsable | Estado Validado | Evidencia en la Conversación |
| :--- | :--- | :-: | :--- |
| **Benchmarking comparativo acústico de Whisper (Small vs Medium vs Large con Ground Truth de YouTube).** | Alejandro Martínez (Alejo) | `completado` | *"Evaluamos las transcripciones sobre el audio patrón contra el Ground Truth oficial de YouTube [...] La conclusión técnica definitiva es que Whisper Medium es nuestro punto dulce [...] Ya quedó consolidado en el informe comparativo tripartito."* |
| **Modularización del Backend FastAPI y migración desde scripts de prototipos.** | Daniel Felipe Castro (Felipe) | `completado` | *"El backend ya está completamente modularizado por capas. Dejamos atrás los scripts aislados de la fase de prototipado e implementamos los controladores REST bajo el estándar empresarial ResponseDto, con modelos relacionales en PostgreSQL..."* |

---

## 🛠️ Decisiones Técnicas y Arquitectónicas Registradas

1. **Selección del Modelo ASR:** Adopción formal de **Whisper Medium** con fragmentación (*Chunking*) de 30 segundos como estándar del pipeline de producción.
2. **Concurrencia en Modo Consenso Dual:** Implementación mediante `ThreadPoolExecutor` para procesar llamadas simultáneas a DeepSeek y OpenAI en paralelo con SLA $< 3\text{ s}$ y tolerancia de discrepancia léxica $\le 20\%$.
3. **Métrica de Auditoría:** Adopción del **WER Ponderado** (Levenshtein penalizando $3.0\times$ entidades críticas como fechas/números/negaciones y $2.0\times$ nombres de responsables).
4. **Catálogo de Pruebas:** Preservar activos los apodos informales (*"Juancho"*, *"Mary"*, *"Carlitos"*) en la base de datos para la demostración en vivo del algoritmo de *Fuzzy Matching*.

---

## 📦 Estructura JSON Canónica para Evaluación Automatizada

```json
{
  "reunion_id": "MEET-SIMULACION-SPRINT-FINAL",
  "archivo_origen": "new-guion.md",
  "total_acuerdos": 3,
  "acuerdos": [
    {
      "id_acuerdo": "AC-GT-001",
      "tarea_desc": "Culminar la integración del panel de Auditoría MLOps en el frontend de Angular (telemetría VACAS con Chaos Testing, calibración WER en vivo, monitor de deriva léxica OOV y Prompt Registry con hash MD5).",
      "responsable_oficial": "Alejandro Martínez",
      "alias_detectado": "Alejo",
      "fecha_compromiso": "2026-11-12T18:00:00",
      "fecha_compromiso_texto": "jueves 12 de noviembre a las 6:00 pm",
      "estado": "pendiente",
      "fragmento_original": "Yo me encargo de culminar la integración del panel de Auditoría MLOps en el frontend de Angular y me comprometo a tenerlo funcionando y conectado con la API a más tardar este jueves 12 de noviembre a las 6:00 de la tarde."
    },
    {
      "id_acuerdo": "AC-GT-002",
      "tarea_desc": "Implementar el endpoint y botón de cancelación segura de procesamientos en curso (liberando memoria y purgando temporales), y estructurar el documento formal de entrega en Word y PDF bajo lineamientos APA 7 completos sin emojis.",
      "responsable_oficial": "Daniel Felipe Castro",
      "alias_detectado": "Felipe",
      "fecha_compromiso": "2026-11-13T14:00:00",
      "fecha_compromiso_texto": "viernes 13 de noviembre a las 2:00 pm",
      "estado": "pendiente",
      "fragmento_original": "Yo me comprometo a implementar el endpoint de cancelación en el backend con su respectivo botón en la interfaz de usuario, y a estructurar el documento formal de entrega en Word y PDF bajo lineamientos APA 7 completos. Entrego ambos entregables probados este viernes 13 de noviembre a las 2:00 de la tarde."
    },
    {
      "id_acuerdo": "AC-GT-003",
      "tarea_desc": "Articular el guion narrativo de sustentación unificando la evolución histórica de los tres cortes del semestre y construir la presentación ejecutiva de soporte (diapositivas finales).",
      "responsable_oficial": "Bryan Betancourt",
      "alias_detectado": "Bryan",
      "fecha_compromiso": "2026-11-14T11:00:00",
      "fecha_compromiso_texto": "sábado 14 de noviembre antes de las 11:00 am",
      "estado": "pendiente",
      "fragmento_original": "Por mi cuenta, yo asumo la responsabilidad de articular el guion narrativo de sustentación unificando la evolución histórica de los tres cortes del semestre y construir la presentación ejecutiva de soporte. Me comprometo a tener listas las diapositivas y el guion definitivo este sábado 14 de noviembre antes de las 11:00 de la mañana."
    }
  ]
}
```

