# 🎭 Guion de Simulación: Reunión de Sprint y Control de Proyecto
> **Proyecto:** Transcriptor Maestro — Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos  
> **Participantes:**  
> - **Bryan Betancourt (Bryan):** Scrum Master & Líder de Frontend / UX  
> - **Daniel Felipe Castro (Felipe):** Arquitecto de Software & Líder Técnico de Backend / IA  
> - **Alejandro Martínez (Alejo):** Ingeniero de MLOps, Datos y Resiliencia  
> **Duración estimada:** 5 minutos y 15 segundos (~850 palabras habladas)

---

### [00:00 - 01:10] Fase 1: Apertura y balance de la evolución técnica

**Bryan:**  
Buenos días, Felipe, Alejo. Iniciamos la sesión de sincronización semanal del proyecto Transcriptor Maestro. Como tenemos la entrega final a la vuelta de la esquina, vamos directo al grano para cerrar en cinco minutos. Revisemos primero los compromisos del ciclo anterior. Alejo, ¿cómo cerraron las pruebas de estrés acústico y la comparativa entre los modelos Whisper que teníamos pendiente en la carpeta de métricas?

**Alejo:**  
Hola, Bryan, buen día. Felipe, qué tal. Les cuento que los resultados fueron contundentes. Evaluamos las transcripciones sobre el audio patrón contra el Ground Truth oficial de YouTube. Whisper Small fue muy rápido con siete segundos, pero perdió términos técnicos en la jerga informal. Luego probamos Whisper Large y, aunque tiene máxima capacidad, nos elevó la latencia a casi cincuenta segundos y presentó truncamiento por memoria al no usar fragmentación. La conclusión técnica definitiva es que Whisper Medium es nuestro punto dulce: alcanzó cien por ciento de cobertura léxica, noventa por ciento de precisión en compromisos y una latencia contenida de veintiocho segundos con fragmentación de treinta segundos. Ya quedó consolidado en el informe comparativo tripartito.

**Bryan:**  
Excelente, decisión validada con datos empíricos. Felipe, por tu lado, ¿cómo quedó la transición desde los cinco prototipos iniciales de Python hacia la arquitectura formal del backend en FastAPI?

**Felipe:**  
Hola, equipo. El backend ya está completamente modularizado por capas. Dejamos atrás los scripts aislados de la fase de prototipado e implementamos los controladores REST bajo el estándar empresarial `ResponseDto`, con modelos relacionales en PostgreSQL y el fallback automático a SQLite por si el motor no responde en local. Además, el orquestador VACAS ya ejecuta la conmutación en caliente entre DeepSeek y la réplica de OpenAI en menos de tres segundos, auditado por el módulo del Perceptrón.

---

### [01:10 - 02:35] Fase 2: Debate técnico y decisiones de ingeniería MLOps

**Bryan:**  
Perfecto, eso nos deja una base sólida. Ahora entremos a resolver los puntos críticos de MLOps y las promesas que adquirimos en el Corte 1 y Corte 2. Felipe, ¿cuál es el estado del Modo Consenso Dual y el manejo de concurrencia?

**Felipe:**  
Puntualmente, teníamos la duda de si lanzar las consultas a los LLMs de forma secuencial o concurrente. Si consultamos primero a DeepSeek y luego a OpenAI en serie, la latencia se nos dispara a más de diez segundos por reunión, lo cual rompe el SLA del sistema. Mi propuesta técnica fue implementar concurrencia real mediante un grupo de hilos con `ThreadPoolExecutor`. De esta manera, ambos modelos procesan la transcripción en paralelo, calculamos la tasa de discrepancia en tiempo real y, si está por debajo del veinte por ciento, fusionamos los acuerdos automáticamente. Si discrepan más, el Perceptrón emite una bandera de alerta para revisión humana.

**Alejo:**  
Apoyo totalmente esa solución, Felipe. Además, desde el frente de MLOps conecté a esa lógica el nuevo Calibrador de WER Ponderado. Ya no calculamos únicamente el error clásico de palabras; ahora aplicamos alineación Levenshtein asignando triple penalización a fechas, números y negaciones, y doble peso a los nombres de los responsables. Si el ASR confunde una fecha de entrega, el sistema no lo trata como un error ortográfico menor, sino como un fallo crítico de seguimiento operativo.

**Bryan:**  
Esa distinción es justo el factor diferencial de nuestro proyecto frente a un simple transcriptor comercial. Tomemos la decisión de una vez: se aprueba la ejecución concurrente en paralelo para el Consenso Dual y dejamos el Calibrador de WER Ponderado como estándar de auditoría del sistema.

---

### [02:35 - 04:00] Fase 3: Asignación de nuevos compromisos y fechas límite

**Bryan:**  
Bien, equipo. Con la arquitectura acordada, definamos las tareas de cierre con responsables directos y fechas inamovibles para la entrega final:

**Bryan:**  
Alejo, tú lideras la infraestructura MLOps. Necesito que dejes integrada la telemetría en la interfaz web de Angular, conectando la vista de auditoría con las cuatro sub-pestañas: telemetría de VACAS con el botón de simulación de fallos por Chaos Engineering, calibración de WER en vivo, el monitor de deriva léxica con vocabulario fuera de dominio y el registro versionado de prompts con hash MD5. ¿Asumes ese compromiso?

**Alejo:**  
Sí, totalmente asumido, Bryan. Yo me encargo de culminar la integración del panel de Auditoría MLOps en el frontend de Angular y me comprometo a tenerlo funcionando y conectado con la API a más tardar este jueves 12 de noviembre a las 6:00 de la tarde.

**Bryan:**  
Anotado. Felipe, de tu parte tenemos dos frentes críticos de estabilidad: primero, descubrimos que si el usuario sube un archivo por error no existía una forma limpia de frenar la tarea; necesitamos el endpoint y el botón en la interfaz para cancelar el procesamiento en curso de inmediato, liberando memoria y purgando los archivos temporales de almacenamiento. Segundo, debemos exportar el documento técnico final bajo normas APA 7 estandarizadas, sin emojis, con tablas de bordes negros y diagramas en alta resolución. ¿Tomas ambas tareas?

**Felipe:**  
De acuerdo, Bryan. Yo me comprometo a implementar el endpoint de cancelación en el backend con su respectivo botón en la interfaz de usuario, y a estructurar el documento formal de entrega en Word y PDF bajo lineamientos APA 7 completos. Entrego ambos entregables probados este viernes 13 de noviembre a las 2:00 de la tarde.

**Bryan:**  
Excelente. Por mi cuenta, yo asumo la responsabilidad de articular el guion narrativo de sustentación unificando la evolución histórica de los tres cortes del semestre y construir la presentación ejecutiva de soporte. Me comprometo a tener listas las diapositivas y el guion definitivo este sábado 14 de noviembre antes de las 11:00 de la mañana.

---

### [04:00 - 05:15] Fase 4: Verificación cruzada, confirmación y cierre

**Felipe:**  
Una duda operativa antes de cerrar, Bryan: para la demostración en vivo ante el jurado, ¿vamos a mantener los apodos coloquiales de prueba como *"Juancho"*, *"Mary"* y *"Carlitos"* en el catálogo de integrantes?

**Alejo:**  
Sí, Felipe, mantengámoslos activos. El algoritmo de Fuzzy Matching con similitud ponderada por encima del setenta y cinco por ciento es uno de nuestros puntos más fuertes en la sustentación, porque demuestra cómo el sistema traduce lenguaje informal de pasillo a registros formales en la base de datos de PostgreSQL.

**Bryan:**  
Exacto, esa demostración es clave. Hagamos un resumen rápido de los compromisos adquiridos hoy:
1. **Alejo Martínez:** Culmina el panel interactivo de Auditoría MLOps con calibración WER, Drift y Chaos Testing para el **jueves 12 de noviembre a las 6:00 pm**.
2. **Daniel Felipe Castro:** Implementa el mecanismo de cancelación segura de procesamientos y consolida el informe técnico APA 7 en PDF para el **viernes 13 de noviembre a las 2:00 pm**.
3. **Bryan Betancourt:** Entrega las diapositivas finales y el guion narrativo articulado para el **sábado 14 de noviembre a las 11:00 am**.

**Bryan:**  
¿Todos conformes con los alcances y tiempos asignados?

**Felipe:**  
Totalmente de acuerdo, claros con las entregas.

**Alejo:**  
De acuerdo por mi parte, sin bloqueos.

**Bryan:**  
Perfecto. Felicitaciones por el trabajo realizado hasta hoy, cerramos la reunión y ¡a avanzar con el cierre del proyecto!

