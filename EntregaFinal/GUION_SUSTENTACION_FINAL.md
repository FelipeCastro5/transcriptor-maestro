# 🎙️ Guion Verbal de Sustentación Final
## Transcriptor Maestro: Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos

* **Asignatura:** Electiva II (Sistemas Inteligentes / MLOps) — Universidad ECCI  
* **Docente:** Ing. Andrés Felipe Duque Montenegro  
* **Integrantes / Expositores:** Bryan Alexander Betancourt Rojas, Daniel Felipe Castro Lizarazo, Alejandro Martínez López  
* **Tiempo Estimado:** 12 a 15 minutos (+ ronda de preguntas)  

---

### Diapositiva 1: Portada Institucional

> *"Muy buenos días, profesor y compañeros. Hoy venimos a presentar la culminación y entrega final de nuestro proyecto **Transcriptor Maestro**. A lo largo del semestre les presentamos la propuesta arquitectónica en el Corte 1 y la fundamentación matemática de los modelos de voz en el Corte 2. Hoy cerramos ese ciclo demostrando cómo materializamos todas las promesas técnicas en una solución de ingeniería completa desplegada en producción.*  
> *En esta presentación verán cómo los modelos de inteligencia artificial evaluados en las fases previas ahora operan dentro de una arquitectura empresarial con alta disponibilidad, resiliencia ante fallos mediante el sistema gemelo VACAS, auditoría con El Perceptrón y control automatizado de proyectos mediante la Curva de Espacios Iguales."*

---

### Diapositiva 2: El Problema Real y Justificación

> *"Como expusimos en el planteamiento inicial de nuestro proyecto, el problema raíz en los equipos de desarrollo es la brecha entre la informalidad de las ceremonias sincrónicas y la rigidez de los sistemas de seguimiento. En aquella ocasión identificamos tres patologías: el dialecto coloquial ('hacer la vuelta', 'yo le jalo'), el sesgo humano al redactar minutas y el olvido de compromisos semana a semana.*  
> *En los cortes anteriores prometimos que la solución no obligaría al usuario a cambiar su forma de hablar; hoy demostramos cómo el sistema escucha la reunión, tolera la jerga conversacional, normaliza las identidades mediante Fuzzy Matching y mantiene viva la trazabilidad temporal de los acuerdos sin intervención manual."*

---

### Diapositiva 3: El Dataset de Audio (Conjunto de Datos)

> *"Recordando la asesoría del Corte 1 y lo sustentado en el Corte 2, el profesor nos hizo un énfasis metodológico fundamental: diferenciar con claridad una base de datos relacional de un **Dataset de Machine Learning**.*  
> *En el Corte 2 les presentamos la estructura de nuestro dataset acústico remuestreado a $16\text{ kHz}$ mono junto con su transcripción patrón de oro (Ground Truth). Para esta entrega final, hemos consolidado dicho dataset integrando una técnica de segmentación en chunks de 30 segundos con un solapamiento (stride) de 5 segundos, resolviendo de forma definitiva los problemas de desbordamiento de memoria (OOM) y las alucinaciones en los bordes temporales que habíamos identificado en las pruebas preliminares."*

---

### Diapositiva 4: Arquitectura General y Flujo de Datos

> *"En la sustentación del Corte 2 les mostramos un diagrama preliminar que concebía el sistema en dos etapas aisladas: transcripción por un lado y extracción por el otro. Para esta entrega final, hemos materializado ese esquema en un pipeline empresarial completamente interconectado y desacoplado.*  
> *El usuario carga el audio desde Angular 19; FastAPI lo procesa de forma asíncrona mediante Background Tasks; Whisper genera la transcripción; el AIHandler aplica las plantillas del Prompt Registry; el módulo Fuzzy Matching resuelve los apodos fonéticos contra PostgreSQL; y El Perceptrón audita en tiempo real cada ejecución, entregando la minuta formalizada y el tablero Kanban en pantalla."*

---

### Diapositiva 5: Estrategia de MLOps y Resiliencia (Sistema Gemelo VACAS)

> *"En el Corte 2 dejamos formulada una promesa de diseño crucial: si íbamos a usar LLMs para procesar minutas, debíamos mitigar la naturaleza de 'caja negra' y la inestabilidad de las APIs públicas mediante un mecanismo de contingencia. En aquel momento planteamos conceptualmente el mecanismo VACAS y El Perceptrón.*  
> *Hoy les mostramos ese sistema 100% construido y operativo: una arquitectura gemela donde si el proveedor primario (DeepSeek) falla, conmuta en caliente en menos de 1.5 segundos a OpenAI; si se pierde internet, se activa la VACA de Emergencia offline basada en reglas lingüísticas; y para sesiones de alta fidelidad, implementamos el Modo Consenso Dual que ejecuta ambos modelos en paralelo y audita su discrepancia léxica."*

---

### Diapositiva 6: Automatización de Proyectos: Curva de Espacios Iguales

> *"En las sesiones de seguimiento anteriores se discutió que el software no podía ser un simple repositorio pasivo que esperara a que el usuario recordara consultar la minuta. En respuesta a esa retroalimentación, desarrollamos la **Curva de Espacios Iguales**.*  
> *Programamos un daemon continuo con APScheduler que realiza barridos periódicos en segundo plano. El algoritmo vigila dos patologías de gestión: las tareas en mora por fecha vencida y, más importante aún, las **Omisiones Sistemáticas** —acuerdos pactados en reuniones previas que llevan dos o más sesiones consecutivas sin volver a mencionarse—, disparando alertas inmediatas en la campana del sistema."*

---

### Diapositiva 7: Evaluación Teórica de Algoritmos (WER & WERw)

> *"Como recordarán de nuestra exposición del Corte 2, dedicamos una investigación profunda a medir matemáticamente las transcripciones palabra por palabra mediante el algoritmo dinámico de Wagner-Fischer sobre 1.504 palabras en Google Colab.*  
> *En esa presentación demostramos que el WER clásico engaña: mientras Whisper Small mostraba un 14.6% aparentemente aceptable, nuestro **WER Ponderado ($WER_w$)** evidenció que el error real de negocio subía al 21.4% por fallar en fechas y negaciones críticas con peso 3.0.*  
> *Ese análisis cuantitativo del Corte 2 fue el que justificó técnicamente la elección de **Whisper Medium** como el motor estándar de nuestro backend: con un WER clásico de $6.51\%$ y un WER ponderado de $8.20\%$, cumplió la meta de estar por debajo del 10% con una latencia inferior a 30 segundos."*

---

### Diapositiva 8: Benchmarking de Rendimiento en Producción (Small vs. Medium vs. Large)

> *"Sin embargo, en el Corte 2 nuestras pruebas se limitaron a una GPU de laboratorio en la nube. Por eso, para esta entrega final nos propusimos responder la pregunta definitiva de ingeniería: ¿qué ocurre con esos mismos tres modelos cuando corren en un entorno de producción real sobre CPU frente a una grabación real de 5 minutos y un Ground Truth sincronizado de YouTube?*  
> *El experimento corroboró de forma contundente lo que habíamos previsto en el Corte 2: Whisper Small fue rápido (3.8 min), pero al recortar 30 segundos de diálogo técnico, el LLM asumió que Steve Jobs era el único responsable del 78% de las tareas, y unió fonéticamente 'Billatkinson' asignándole la tarea erróneamente a Burrell Smith.*  
> *Whisper Large logró una síntesis ejecutiva impecable de 6 acuerdos pero tardó 24 minutos en CPU. Por tanto, confirmamos empíricamente que **Whisper Medium** es el punto de balance óptimo para producción: capturó el 99.2% del diálogo y permitió delegar equilibradamente las responsabilidades con 95% de confianza Fuzzy."*

---

### Diapositiva 9: Demostración en Vivo (Live Demo)

> *"A continuación, pasamos a la demostración en vivo de la plataforma desplegada en nuestro entorno local, donde podrán ver articulados todos los componentes que fuimos construyendo y validando corte a corte.*  
> *(El compañero muestra la pantalla) Vamos a procesar un audio seleccionando la Estrategia 5 con el Modo Consenso Dual activado.*  
> *Como pueden observar, el sistema transcribe el audio, extrae los acuerdos y resuelve las identidades mediante Fuzzy Matching con su score de confianza.*  
> *Si abrimos la campana de notificaciones, podemos ejecutar en vivo el barrido de la Curva de Espacios Iguales para auditar moras y omisiones históricas.*  
> *Y finalmente, en la pestaña de Auditoría MLOps, verán operando en tiempo real la matriz de Levenshtein coloreada token por token (aciertos en verde, sustituciones en rojo y omisiones en amarillo), demostrando que la teoría matemática del Corte 2 está completamente implementada en el software."*

---

### Diapositiva 10: Conclusiones y Cumplimiento

> *"Para concluir esta sustentación:*  
> *Primero: cerramos con éxito la trayectoria del proyecto. Pasamos del diagnóstico conceptual en el Corte 1, a la rigurosa calibración matemática de ASR en el Corte 2, y hoy entregamos un software de producción robusto, desacoplado y resiliente.*  
> *Segundo: demostramos que las métricas de negocio como el WER ponderado y los mecanismos de alta disponibilidad como VACAS son indispensables para llevar inteligencia artificial generativa a entornos reales de ingeniería.*  
> *Tercero: cubrimos el 100% de los compromisos adquiridos en la asignatura con código limpio, arquitectura basada en microservicios y repositorio auditable.*  
> *Agradecemos al docente por las retroalimentaciones en cada corte que guiaron la evolución del sistema. Quedamos atentos a sus preguntas. Muchas gracias."*

---

### Anexo: Banco de Respuestas Técnicas (Preguntas Probables del Jurado)

#### ❓ Pregunta 1: "¿Por qué en su proyecto dicen que tienen un Dataset y no una Base de Datos?"
* **Respuesta:** *"Profesor, como usted nos aclaró en la asesoría del Corte 1, una base de datos relacional (como nuestro PostgreSQL) es una herramienta de persistencia transaccional del software. Nuestro **Dataset de Machine Learning** son los archivos de audio en formato WAV/MP3 remuestreados a 16 kHz mono con sus respectivas transcripciones humanas estrictas (Ground Truth) y etiquetas de tareas. Las tablas de Postgres son solo el repositorio del sistema web, pero el dataset es la fuente con la que evaluamos y calibramos los modelos."*

#### ❓ Pregunta 2: "¿Cómo calculan exactamente el WER ponderado y por qué una negación pesa 3.0?"
* **Respuesta:** *"El WER clásico es $(S + D + I) / N$. En el WER ponderado asignamos pesos a cada tipo de token según su criticidad. Una negación como 'no' pesa $3.0$ porque si Whisper omite la palabra 'no' en la frase 'Juan debe entregar el informe' frente a 'Juan NO debe entregar el informe', el LLM extraería una tarea completamente opuesta. El error en una palabra común es trivial, pero en una negación altera la semántica de forma catastrófica; por eso su peso relativo es diez veces mayor que el de un artículo (que pesa 0.3)."*

#### ❓ Pregunta 3: "¿Cómo funciona la alineación de Levenshtein por debajo?"
* **Respuesta:** *"Implementamos el algoritmo dinámico de Wagner-Fischer sobre listas de palabras normalizadas. Se construye una matriz $D[i, j]$ de tamaño $(N+1) \times (M+1)$ donde cada celda calcula el costo mínimo entre sustitución ($D[i-1, j-1] + \text{costo}$), eliminación ($D[i-1, j] + 1$) e inserción ($D[i, j-1] + 1$). Luego hacemos backtracking desde la esquina inferior derecha para reconstruir el alineamiento óptimo que minimiza la distancia total de edición."*

#### ❓ Pregunta 4: "¿Qué es la Curva de Espacios Iguales y cómo la programaron?"
* **Respuesta:** *"Es el principio de control periódico continuo. En lugar de esperar a que un usuario consulte la app, programamos un BackgroundScheduler con APScheduler que corre periódicamente. Este scheduler revisa dos condiciones: compromisos cuya fecha límite ya pasó (atrasos) y compromisos que llevan 2 o más reuniones consecutivas del mismo proyecto sin ser mencionados (omisiones). Ambas patologías generan alertas en la base de datos y se reflejan en la campana de la interfaz."*

#### ❓ Pregunta 5: "¿Cómo abordan el problema de que los LLMs son cajas negras?"
* **Respuesta:** *"Tal como se vio en la clase 14, las redes neuronales y los LLMs pueden presentar desviaciones impredecibles. Nosotros mitigamos la caja negra con cuatro barreras: primero, tipado estricto en la salida forzando validación Pydantic; segundo, el Modo Consenso Dual donde votan dos modelos distintos (DeepSeek y OpenAI) y alertamos si discrepan más del 20%; tercero, El Perceptrón que audita latencias y clasifica errores; y cuarto, el fallback automático a reglas lingüísticas deterministas y offline si los modelos fallan."*

#### ❓ Pregunta 6: "¿Qué ocurrió experimentalmente cuando compararon Whisper Small, Medium y Large sobre el mismo audio en vivo?"
* **Respuesta:** *"Profesor, comprobamos empíricamente que la resolución acústica condiciona la semántica del LLM. Con Whisper Small ahorramos 67% de tiempo de CPU (3.8 min vs 11.5 min), pero al recortar 30 segundos donde el equipo hablaba, el LLM asumió que Steve Jobs era el único responsable del 78% de las tareas, y unió fonéticamente 'Billatkinson' confundiéndolo con Burrell Smith. En cambio, Whisper Medium y Large preservaron la réplica del equipo, permitiendo una asignación equilibrada entre Steve Jobs y el equipo de diseño con 95% de confianza en el catálogo Fuzzy. Large además reconoció históricamente el proyecto 'Lisa' y sintetizó 6 acuerdos directivos de nivel C-Level. Esto justifica técnicamente por qué Medium es nuestro modelo de despliegue predeterminado."*

