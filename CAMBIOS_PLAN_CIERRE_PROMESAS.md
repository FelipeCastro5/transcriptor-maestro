# 📋 Informe de Cambios: Plan de Implementación de Cierre de Promesas

> **Proyecto:** Transcriptor Maestro — Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos  
> **Asignatura:** Electiva II - Sistemas Inteligentes / MLOps (Universidad ECCI)  
> **Fecha de Finalización:** Noviembre 2026  
> **Estado:** 100% Implementado, Integrado y Verificado  

---

## 🎯 1. Objetivo del Documento

Este documento técnico detalla los cambios de arquitectura, algoritmos, endpoints y componentes de interfaz implementados en el monorepositorio `prototipos` a partir del [**Plan de Implementación de Cierre**](../EntregaFinal/plan-implementacion-cierre.md). 

El objetivo primordial de esta intervención fue subsanar la totalidad de las brechas técnicas identificadas en la [**Evaluación de Promesas vs Avance Real**](../EntregaFinal/evaluacion-promesas-parte1.md), alcanzando el **100% de cumplimiento funcional y de MLOps** de cara a la sustentación y entrega final de la materia.

---

## 📊 2. Matriz de Cierre de Brechas (Antes vs. Después)

| # | Compromiso / Promesa Evaluada | Estado Previo | Estado Actual | Solución Técnica Implementada |
| :-: | :--- | :-: | :-: | :--- |
| **1** | **Curva de Espacios Iguales** (Barrido periódico de fechas y omisiones) | 🟡 50% | 🟢 **100%** | `SystemScheduler` en background (`APScheduler`), disparador a medianoche y detección de omisiones ($\ge 2$ reuniones). |
| **2** | **Sistema de Alertas y Notificaciones** (Atrasos, omisiones y webhooks) | 🟡 40% | 🟢 **100%** | `AlertService` con persistencia en `alertas_sistema`, despacho webhook (Discord/Slack/Mock) y campana interactiva en Angular. |
| **3** | **Calibración de WER y WER Ponderado ($WER_w$) en Vivo** | 🔴 0% | 🟢 **100%** | `EvalService` con alineación Levenshtein exacta token a token, métricas completas ($S, D, I, H$, Precisión, Longitud Relativa) y persistencia en `evaluaciones_calibracion`. |
| **4** | **Monitoreo de Data Drift Lingüístico** | 🔴 0% | 🟢 **100%** | Algoritmo de detección Out-Of-Vocabulary (OOV) con base léxica corporativa y detección de modismos coloquiales colombianos. |
| **5** | **Prompt & Model Registry Versionado** | 🔴 0% | 🟢 **100%** | Catálogo `PromptRegistry` con plantillas versionadas (`v1_base`, `v2_informal`, `v3_hibrido`), hashes MD5 inmutables y activación en caliente. |
| **6** | **Modo Consenso Concurrente en VACAS** | 🟡 75% | 🟢 **100%** | Invocación paralela (`ThreadPoolExecutor`) de DeepSeek y OpenAI con métrica de discrepancia ($\le 20\%$) y alerta Perceptrón Nivel 2. |
| **7** | **Visualización e Integración en Frontend** | 🟡 70% | 🟢 **100%** | Campana `🔔` con drawer de alertas, vista de diff Levenshtein coloreada, barra de data drift y switch de consenso en Angular 19. |

---

## 🛠️ 3. Cambios Técnicos Detallados por Fase

### 🕒 FASE 1: Curva de Espacios Iguales & Sistema de Alertas

#### Componentes Creados:
- **`backend/app/core/scheduler.py`**:
  - Implementación de `SystemScheduler` utilizando `APScheduler.schedulers.background.BackgroundScheduler`.
  - Diseñado para ejecutarse periódicamente en segundo plano dentro del mismo proceso FastAPI, sin requerir workers externos pesados (como Celery/Redis).
  - Admite activación automática continua o ejecución bajo demanda ante el jurado (`ejecutar_barrido_ahora()`).
- **`backend/app/services/alert_service.py`**:
  - Emite alertas con severidades `CRITICAL`, `WARNING` e `INFO`.
  - Despacha notificaciones en vivo hacia `ALERT_WEBHOOK_URL` (Discord / Slack) o simulador corporativo en logs y PostgreSQL.
  - Métodos para consultar alertas activas, contar no leídas y marcar alertas como leídas.
- **`backend/app/db/models/alerta.py`**:
  - Modelo SQLAlchemy `AlertaSistema` mapeado a la tabla `alertas_sistema`.
- **`backend/app/schemas/alerta.py`**:
  - Esquemas Pydantic `AlertaResponse`, `BarridoResultadoResponse` y `SchedulerStatusResponse`.

#### Componentes Modificados:
- **`backend/app/main.py`**:
  - Incorporado manejador de ciclo de vida asíncrono (`lifespan`) para inicializar la base de datos y arrancar el scheduler al levantar la API, apagándolo ordenadamente al cerrar el proceso.
- **`backend/app/services/reunion_service.py`**:
  - Añadido el método `ejecutar_barrido_acuerdos_periodico(db)`:
    - Escanea todos los acuerdos en estado `pendiente`.
    - Detecta compromisos con fecha vencida y los actualiza a `atrasado`, registrando el evento en `historial_estados`.
    - Detecta **omisiones**: si el compromiso no ha sido mencionado en $\ge 2$ reuniones posteriores de su mismo proyecto, emite alerta `CRITICAL` con recomendación de reprogramación.
- **`backend/app/api/v1/endpoints/sistema.py`**:
  - Expuestos los endpoints `GET /alertas`, `POST /alertas/{id}/marcar-leida`, `GET /scheduler/estado` y `POST /scheduler/ejecutar`.
- **`db/db.sql`**:
  - Añadida la definición DDL de la tabla `alertas_sistema` con sus respectivos índices.

---

### 🧪 FASE 2: MLOps en Vivo — Calibrador de WER, Data Drift y Prompt Registry

#### Componentes Creados:
- **`backend/app/services/eval_service.py`**:
  - **Alineación Levenshtein (Wagner-Fischer):** Algoritmo de programación dinámica token por token que genera la matriz de operaciones óptima (`MATCH`, `SUBSTITUTION`, `DELETION`, `INSERTION`).
  - **WER Clásico:**
    $$\text{WER} = \frac{S + D + I}{N}$$
  - **WER Ponderado ($\text{WER}_w$):**
    $$\text{WER}_w = \frac{\sum (w_{\text{op}} \times \text{error})}{\sum (w_{\text{ref}} \times \text{token}_{\text{GT}})}$$
    Aplicando los pesos documentados en el Sprint 2:
    - Fechas, números y negaciones: **3.0**
    - Nombres propios de personas: **2.0**
    - Verbos de acción y sustantivos clave: **1.5**
    - Artículos, preposiciones y muletillas: **0.3**
    - Palabras comunes: **1.0**
  - **Métricas Complementarias:** Precisión de palabra ($\frac{H}{N}$), Longitud Relativa ($\frac{N_{hyp}}{N_{ref}}$) y estado de calidad (`OPTIMO` si $\text{WER} \le 10\%$, `ACEPTABLE` si $< 25\%$, `CRITICO` si $\ge 25\%$).
  - **Detección de Data Drift:** Analizador de palabras *Out-Of-Vocabulary* (OOV) contra vocabulario corporativo y de Scrum, emitiendo diagnósticos automáticos (`ESTABLE`, `MODERADO`, `CRITICO_DRIFT`).
- **`backend/app/core/prompt_registry.py`**:
  - Gestor de versiones inmutables de prompts:
    - `PRM-V1-BASE` (v1.0.0): Prompt base formal corporativo.
    - `PRM-V2-INFORMAL` (v2.1.0): Especializado en modismos colombianos (*"hacer la vuelta"*, *"camello"*, *"yo le jalo"*).
    - `PRM-V3-HIBRIDO` (v3.0.0): Modelo avanzado multi-dominio con detección de dependencias y compromisos implícitos.
  - Cada versión calcula automáticamente su **Hash MD5** inmutable para auditoría.
- **`backend/app/db/models/evaluacion.py`**:
  - Modelo `EvaluacionCalibracion` mapeado a la tabla `evaluaciones_calibracion`.
- **`backend/app/schemas/evaluacion.py`**:
  - Esquemas de request/response para calibración de WER, análisis de drift y catálogo de prompts.

#### Componentes Modificados:
- **`backend/app/api/v1/endpoints/auditoria.py`**:
  - Añadidos los endpoints:
    - `POST /calibrar-wer`: Ejecuta la alineación y guarda la telemetría en PostgreSQL.
    - `GET /calibraciones`: Consulta el historial de benchmarks realizados.
    - `POST /data-drift`: Evalúa la desviación léxica del texto suministrado o de una reunión grabada.
    - `GET /prompts-historial`: Lista las versiones del catálogo con sus hashes.
    - `POST /prompts-activar`: Activa una versión de prompt en caliente para las siguientes inferencias.
- **`backend/app/services/ai_handler.py`**:
  - Vinculado con `prompt_registry` para seleccionar dinámicamente la plantilla activa o específica de la estrategia seleccionada.
- **`db/db.sql`**:
  - Añadida la tabla `evaluaciones_calibracion` con campos para métricas numéricas y detalles de alineación en formato `JSONB`.

---

### 🛡️ FASE 3: Alta Disponibilidad — Consenso Dual Concurrente en VACAS

#### Componentes Modificados:
- **`backend/app/services/vacas.py`**:
  - Implementado el parámetro `modo_consenso: bool = False` en `ejecutar_con_conmutacion()`.
  - Método `_calcular_discrepancia(texto1, texto2)` que evalúa la distancia de edición relativa a nivel de tokens entre las respuestas de ambos LLMs.
  - **Invocación Concurrente con `ThreadPoolExecutor`:** Dispara DeepSeek (`deepseek-chat`) y OpenAI (`gpt-4o-mini`) en hilos paralelos con un timeout estricto de $3.5\text{s}$.
  - **Evaluación de Consenso:**
    - Si ambos responden y $\text{Discrepancia} \le 0.20$ ($20\%$ de SLA): Se considera consenso total, registrando `NivelError.NIVEL_4_INFORMATIVO` (éxito).
    - Si la discrepancia supera el $20\%$: El Perceptrón clasifica la inferencia como `NivelError.NIVEL_2_MEDIO` (*Warning por Divergencia Cognitiva*) y conserva la respuesta primaria con advertencia en telemetría.
    - Si un proveedor cae o no tiene API key configurada: Conmuta en caliente al sobreviviente sin interrumpir la operación.
    - Si ambos fallan: Conmuta a la VACA de Emergencia (`OFFLINE_RULES`).
- **`backend/app/schemas/reunion.py`**:
  - Añadido el atributo `modo_consenso: bool = False` en `ProcesarReunionRequest`.
- **`backend/app/api/v1/endpoints/reuniones.py`**:
  - Parametrizado `modo_consenso` tanto en la subida automática (`/upload`) como en el reprocesamiento manual (`/{id}/procesar`).
- **`backend/app/services/reunion_service.py`** y **`backend/app/services/ai_handler.py`**:
  - Propagado el flag `modo_consenso` a lo largo de todo el pipeline de análisis.

---

### 🎨 FASE 4: Integración en Frontend (Angular 19)

#### Componentes Modificados:
- **`frontend-angular/src/app/core/models.ts`**:
  - Interfaces TypeScript para `AlertaSistema`, `SchedulerStatus`, `BarridoResultado`, `CalibrarWER`, `AlineacionToken`, `DataDrift`, `PromptVersion` y extensión de `ConfigIA` con `modo_consenso`.
- **`frontend-angular/src/app/core/api.service.ts`**:
  - Métodos HTTP agregados para invocar los endpoints de alertas, scheduler, calibración de WER, análisis de data drift y gestión de prompts.
- **`frontend-angular/src/app/app.component.ts`**:
  - Barra superior (*Topbar*) enriquecida con icono de campana `🔔` y badge reactivo con el total de alertas activas no leídas.
  - Drawer deslizante interactivo con la lista de compromisos en riesgo/omisión, botón para marcar como leída y botón de ejecución manual: **"⚡ Ejecutar Curva Espacios Iguales"**.
- **`frontend-angular/src/app/pages/auditoria.component.ts`**:
  - Rediseñado en 4 sub-pestañas:
    1. **Telemetría VACAS:** Métricas de latencia, tasa de éxito y botón de simulación de fallo (*Chaos Testing*).
    2. **Calibración de WER & WER Ponderado:** Formulario para comparar Ground Truth vs Hipótesis con botón de carga de caso de prueba. Tarjetas de métricas ($WER$, $WER_w$, Precisión, Longitud) y **visualizador de alineación Levenshtein coloreado token a token** (`MATCH` en verde, `SUBSTITUTION` en rojo, `DELETION` en amarillo, `INSERTION` en morado).
    3. **Detección de Data Drift:** Indicador visual de porcentaje OOV, recomendaciones automáticas y etiquetas de modismos o palabras no indexadas.
    4. **Prompt Registry:** Vista de tarjetas con versión, MD5 hash y botón para **"Activar en Caliente"** en producción.
- **`frontend-angular/src/app/pages/subir.component.ts`**:
  - Añadido interruptor visual: **"Modo Consenso Dual (DeepSeek + OpenAI)"** con explicación del SLA de $3\text{s}$ y tolerancia a discrepancia.

---

## 🔬 4. Verificación y Resultados de Pruebas

Se ejecutó una suite de pruebas integradas de extremo a extremo ([`test_pipeline_completo.py`](./backend/test_pipeline_completo.py)), arrojando resultados satisfactorios:

```text
[DB] Conectado exitosamente a: localhost:5432/transcriptor_db
=== 1. VERIFICANDO SALUD DEL SERVICIO ===
Health OK: Status 200 (Online)

=== 2. FASE 1: CURVA DE ESPACIOS IGUALES & ALERTAS ===
Scheduler Estado: {'activo': True, 'modo': 'DEMOSTRACION_CONTINUA_ESPACIOS_IGUALES'}
Barrido Ejecutado: 76 alertas generadas (compromisos atrasados y omisiones detectadas)
Total Alertas en Sistema: 76 activas en PostgreSQL

=== 3. FASE 2: MLOPS - WER, DATA DRIFT Y PROMPT REGISTRY ===
WER Clásico: 10.0% (Dentro del SLA meta del proyecto)
WER Ponderado (WER_w): 18.87% (Ponderando fechas y negaciones)
Alineación Tokens: 10 tokens alineados palabra por palabra
Data Drift Estado: MODERADO (OOV: 27.27%)
Prompt Registry: 3 versiones cargadas con MD5 Hash inmutable

=== 4. FASE 3: CONSENSO DUAL VACAS ===
Discrepancia entre respuestas evaluada: 16.67% (<= 20% SLA Cumplido)

>>> TODAS LAS FASES FUNCIONANDO AL 100% <<<
```

Asimismo, se verificó la compilación de la aplicación Angular 19 en modo producción:
```text
> ng build
Application bundle generation complete. [2.738 seconds]
Output location: dist/frontend-angular (0 errores)
```

---

## 🚀 5. Cómo Demostrarlo en la Sustentación Final

1. **Curva de Espacios Iguales:**
   - Hacer clic en la campana `🔔` en la barra superior del Frontend.
   - Pulsar el botón **"⚡ Ejecutar Curva Espacios Iguales"**: se observará en tiempo real la detección de compromisos vencidos y el despacho de alertas.
2. **Calibración de WER y Data Drift:**
   - Navegar a la pestaña **"Auditoría MLOps"**.
   - Ir a la sub-pestaña **"Calibración de WER"** y pulsar *"Cargar Caso de Demostración"*.
   - Hacer clic en *"Ejecutar Calibración"*: se desplegará el diff palabra por palabra y las tarjetas con $WER$ y $WER_w$.
   - Ir a la sub-pestaña **"Data Drift"** y pulsar *"Cargar Audio Coloquial Colombiano"*: se visualizarán los términos fuera de vocabulario (*"camello"*, *"hacer la vuelta"*).
3. **Prompt Registry:**
   - Ir a la sub-pestaña **"Prompt Registry"**: alternar la versión activa haciendo clic en *"Activar en Caliente"*.
4. **Consenso Dual VACAS:**
   - Ir a la pestaña **"Subir reunión"**, marcar la casilla *"Modo Consenso Dual"* y procesar una grabación: la auditoría registrará la ejecución paralela y el cálculo de discrepancia léxica.
