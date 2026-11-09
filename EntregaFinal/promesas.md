Analyzed instrucciones-finales.md:L1-8

Para tener total claridad ante el profesor y el jurado, aquí tienes el desglose exacto de **qué se prometió en el Primer Corte**, **qué se definió y probó en el Segundo Corte**, y **cómo se conecta todo con la Entrega Final**.

---

## 🎯 1. PRIMER CORTE: La Gran Promesa del Proyecto (La Presentación y Documento Base)

En el primer corte presentaron la visión del producto y la arquitectura teórica. Lo que allí prometieron se resume en **5 pilares fundamentales**:

### A. La Promesa Central de Valor
* **No ser un simple transcriptor:** Se prometió que el sistema no sería como *Teams* o *Otter.ai* (que solo botan texto plano), sino un **"Sistema con Memoria"**:
  1. Extrae los acuerdos de la reunión actual (*Tarea, Responsable, Fecha*).
  2. Los guarda en una base de datos.
  3. En la siguiente reunión, el sistema es capaz de contrastar si lo pactado la semana pasada **se cumplió, sigue pendiente o está atrasado**.

### B. Las 3 Inteligencias del Sistema
Prometieron que el sistema operaba bajo 3 tipos de inteligencia:
1. **Inteligencia Lingüística (NLP):**
   * Transcripción de audio a texto usando **Whisper en local** (On-Premise).
   * Extracción de tareas estructuradas en JSON usando un **LLM** (DeepSeek / Hugging Face).
2. **Inteligencia Lógico-Matemática:**
   * Máquina de estados: ciclo de vida del acuerdo (*Pendiente $\rightarrow$ Completado / Atrasado*).
   * Algoritmo de emparejamiento (*Fuzzy Matching* con distancia de Levenshtein) para no duplicar tareas y corregir nombres mal pronunciados.
3. **Inteligencia Interpersonal:**
   * Métrica de cumplimiento por miembro del equipo ($\text{Completadas} / \text{Asignadas}$).
   * Detección de **omisiones** (compromisos que nadie volvió a mencionar en reuniones posteriores).

### C. La "Arquitectura Híbrida Real" (Privacidad por Diseño)
* **La regla de oro:** El archivo de audio crudo **NUNCA abandona la computadora local** (por secretos comerciales y privacidad de la voz).
* A la nube solo viaja el texto plano de la transcripción (pocos kilobytes) para que el LLM extraiga el JSON.

### D. Principios de Automatización y MLOps (Las Clases del Profesor)
Prometieron aplicar rigurosamente las reglas de automatización vistas en la materia:
* **Estados Binarios Absolutos:** Cada etapa solo tiene dos salidas: `0` (Éxito) o `1` (Fallo). No hay términos medios.
* **Sistema VACAS (Variables de Respaldo Gemelas):** Si el LLM primario falla por timeout ($> 3\text{ s}$) o error 500, el sistema debe conmutar en caliente a un LLM réplica en $< 1.5\text{ segundos}$ para que la operación nunca se detenga.
* **El Perceptrón (Megatron):** Un auditor que vigila la latencia en milisegundos y clasifica los errores en una **Jerarquía de Niveles 0 al 4** (desde Nivel 0 Catastrófico hasta Nivel 4 Informativo).
* **Anti-Alucinación:** Obligar al LLM a devolver el campo `fragmento_original` (la frase textual exacta de la reunión) para que el humano audite y confirme que la IA no inventó la tarea.

### E. Metas Estadísticas y Operativas (SLOs Iniciales)
* $\text{WER} < 10\%$ en la transcripción.
* $F_1\text{-Score} > 0.85$ en la extracción del JSON.
* Latencia del LLM $< 3\text{ segundos}$ y conmutación a respaldo en $< 1.5\text{ segundos}$.
* Procesar 1 hora de audio en menos de 10 minutos.

---

## 🔬 2. SEGUNDO CORTE: Las Pruebas Experimentales y el Marco Matemático

En el segundo corte, el tutor les ordenó **enfocarse en evaluar exhaustivamente la Etapa 1 (Whisper)** antes de pasar a la integración completa, argumentando: *"Si la transcripción es basura, el LLM va a procesar basura y alucinará tareas"*.

### A. Lo que se prometió y definió en Métricas
Diseñaron un marco formal de **10 métricas matemáticas palabra por palabra**:
1. **$M1$ — $\text{WER}$ (Word Error Rate):** $\frac{S + D + I}{N}$ (Sustituciones, Eliminaciones, Inserciones sobre el total de palabras del Ground Truth).
2. **$M2$ — Precisión:** $1 - \text{WER}$.
3. **$M3$, $M4$, $M5$ — Tasas desglosadas:** $\text{Deletion Rate}$ (palabras comidas), $\text{Substitution Rate}$ (palabras cambiadas), $\text{Insertion Rate}$ (palabras inventadas).
4. **$M6$ — Longitud Relativa:** Ratio palabras predicción vs Ground Truth (para detectar si el modelo omite o habla de más).
5. **$M7$ — $\text{WER}_w$ (WER Ponderado) — *La Métrica Estrella*:**
   * Entendieron que errar en la palabra *"el"* es inocuo, pero errar en *"viernes"* (fecha) o en *"no"* (negación) es fatal.
   * Asignaron pesos matemáticos: artículos ($0.3$), palabras comunes ($1.0$), verbos clave ($1.5$), nombres propios ($2.0$), fechas/números/negaciones ($3.0$).
6. **Métricas Operativas:** Tiempo total, consumo de RAM y tasa de cuelgues ($OOM$).

### B. El Experimento Real (Caso "Pesquera Diamante")
* Se tomó un audio real de 8 minutos, 6 participantes, jerga pesquera y microcortes de red.
* Se elaboró el **Ground Truth manual** ($N = 1458$ palabras).
* Se corrieron **9 pruebas** en Google Colab (3 corridas con `Small`, 3 con `Medium`, 3 con `Large`).

### C. Lo que arrojaron las pruebas y el "Criterio de Ingeniería"
| Modelo | Tiempo Promedio | $\text{WER}$ Promedio | Precisión | $\text{WER}_w$ Ponderado | Hallazgo Crítico |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Small** | $7\text{ min }28\text{ s}$ | $13.7\%$ | $86.3\%$ | $17.8\%$ | Rápido, pero deforma nombres (*"Seren"* en vez de *"Edwin"*). |
| **Medium** | $26\text{ min }26\text{ s}$ | $11.1\%$ | $88.9\%$ | $14.9\%$ | **El más balanceado:** longitud casi perfecta ($0.99$) y sin bucles. |
| **Large** | $61\text{ min }01\text{ s}$ | **$8.7\%$** | **$91.3\%$** | **$11.4\%$** | El más preciso, pero tardó más de 1 hora y tuvo **alucinaciones severas por repetición** (repetía frases 4 veces seguidas). |

* **La conclusión acordada con el tutor:** El profesor les dijo: *"Ustedes eligen por criterio de ingeniería (costo, tiempo, precisión). Penalicen las alucinaciones"*. 
* Por ende, la promesa para el cierre fue: **Adoptar `Medium` como modelo base**, y para mitigar sus errores fonéticos en nombres, resolverlos mediante el **Fuzzy Matching de Levenshtein** en la siguiente etapa.

---

## 🏁 3. CÓMO SE CONECTA TODO ESTO CON LA ENTREGA FINAL (Tercer Corte)

El tutor dejó muy claro en el archivo `instrucciones-finales.md` lo que evalúa en esta entrega:

```text
Para entrega final:
1. Flujo de datos
2. MLOps
3. DevOps
Entregar en un repositorio de GitHub: README del programa, documento del proyecto, presentación y código fuente.
```

### ¿Cómo demuestran que cumplieron todo lo prometido?

| Promesa Inicial (Cortes 1 y 2) | ¿Cómo se cumplió en el sistema final? | Dónde mostrarlo en la sustentación |
| :--- | :--- | :--- |
| **1. Flujo de Datos Extremo a Extremo** | El usuario sube audio o `.txt` en el Drag & Drop de Angular $\rightarrow$ el backend procesa asíncronamente con Whisper $\rightarrow$ el LLM extrae acuerdos y resumen $\rightarrow$ se guarda en PostgreSQL $\rightarrow$ el front muestra la Minuta con citas y el Kanban. | En vivo desde **`http://localhost:4200`** (Vista `/subir` y `/minuta`). |
| **2. Privacidad y Modelo Whisper Parametrizable** | Whisper corre en local; se puede elegir entre `small`, `medium` o `large` y bypass con `.txt`. | En el selector de la pantalla `/subir` y en `ai_handler.py`. |
| **3. Sistema VACAS (Tolerancia a fallos)** | Conmutación real entre DeepSeek y OpenAI con fallback local de emergencia. | En la pestaña `/auditoria`, activando el interruptor de **"Simular Fallo VACAS"** para ver cómo conmuta en milisegundos. |
| **4. El Perceptrón y Jerarquía 0–4** | Monitorea la latencia y registra cada llamada en la tabla `auditoria_ia_logs`. | En el panel de métricas de telemetría de `/auditoria`. |
| **5. Inteligencia 2 (Fuzzy Matching)** | Mitiga el error de Whisper en nombres usando Levenshtein contra el catálogo oficial y alias. | En la columna *"Responsable"* de la tabla de acuerdos, mostrando el badge de porcentaje de coincidencia. |
| **6. Seguimiento con Memoria** | Tablero Kanban donde las tareas pasan a *Completado* o *Atrasado*. | En la pestaña `/acuerdos` de la interfaz web. |
| **7. DevOps y MLOps** | Arquitectura desacoplada, gestión y limpieza de caché de modelos locales, Git Flow (`bryan/front` $\rightarrow$ `main`). | En la vista de caché (`/auditoria`) y en el repositorio de GitHub. |

Con este esquema tienes el hilo conductor perfecto: en el **Corte 1** prometieron la arquitectura y las reglas de negocio; en el **Corte 2** hicieron los experimentos matemáticos y seleccionaron el modelo ideal; y en el **Corte 3** construyeron la plataforma completa que hace realidad cada una de esas promesas.