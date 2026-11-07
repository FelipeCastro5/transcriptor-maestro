# 📋 PLAN DE IMPLEMENTACIÓN: CIERRE DE BRECHAS MLOPS & AUTOMATIZACIÓN
## Proyecto: Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos ("Transcriptor Maestro")

* **Universidad:** Universidad ECCI — Facultad de Ingeniería — Ingeniería de Sistemas
* **Asignatura:** Electiva II (Sistemas Inteligentes / MLOps)
* **Docente:** Ing. Andrés Felipe Duque Montenegro
* **Autores:** Bryan Alexander Betancourt Rojas, Daniel Felipe Castro Lizarazo, Alejandro Martínez López
* **Fecha de formulación:** Noviembre de 2026

---

## 🎯 1. OBJETIVO GENERAL Y ESTRATEGIA DE TRABAJO

El objetivo de este plan es **cubrir y elevar al 100% de cumplimiento operativo y sustentable** las 7 brechas identificadas en el análisis crítico ([`evaluacion-promesas-parte1.md`](file:///c:/MisProyectos/ECCI/trasncriptor%20maestro/EntregaFinal/evaluacion-promesas-parte1.md)). 

Se distribuye en **4 fases secuenciales y modulares** que permiten repartir el trabajo entre los 3 integrantes del equipo (**Bryan, Daniel y Alejandro**), manteniendo siempre la estabilidad del sistema actual y garantizando que el proyecto se ejecute de forma autónoma y sin fricciones en un entorno local (Windows / FastAPI / PostgreSQL / Angular 19).

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ROADMAP DE IMPLEMENTACIÓN POR FASES                                  │
├────────────────────┬──────────────────────────────────────┬────────────────────────┬───────────────────┤
│ Fase               │ Foco / Componentes Clave             │ Brechas que cubre      │ Responsable Sug.  │
├────────────────────┼──────────────────────────────────────┼────────────────────────┼───────────────────┤
│ Fase 1: Cron & Web │ Curva Espacios Iguales + Alertas     │ Brechas 5 y 6 (50%→100%│ Backend / Daniel  │
│ Fase 2: MLOps Core │ Data Drift + WER Vivo + Registry     │ Brechas 3 y 4 (60%→100%│ IA-Data / Alejandro│
│ Fase 3: VACAS Dual │ Modo Consenso Concurrente (asyncio)  │ Brecha 2 (75%→100%)    │ Backend / Daniel  │
│ Fase 4: Frontend   │ Paneles en Angular 19 + Demo Final   │ Integración UI global  │ Frontend / Bryan  │
└────────────────────┴──────────────────────────────────────┴────────────────────────┴───────────────────┘
```

---

## 📅 FASE 1: AUTOMATIZACIÓN PERIÓDICA Y SISTEMA DE ALERTAS (CURVA DE ESPACIOS IGUALES)
> **Brechas cubiertas:** Brecha 5 (Curva de Espacios Iguales / Scheduler) y Brecha 6 (Escalamiento y Alertas Externas).  
> **Estimación de esfuerzo:** 1.5 a 2 días de desarrollo.  
> **Responsable sugerido:** Daniel Felipe Castro (Backend & Arquitectura).

### 1.1. Contexto y Justificación
En el documento teórico de la materia se prometió una **Curva de Control de Espacios Iguales** (revisión periódica cada medianoche) para recalcular atrasos y emitir alertas. Actualmente el cálculo se hace bajo demanda (*On-Request*). Implementaremos un motor de ejecución en segundo plano sin dependencias de servicios externos pesados.

### 1.2. Tareas Técnicas Detalladas
1. **Integración de `APScheduler` en FastAPI:**
   * Archivo: `backend/app/core/scheduler.py`.
   * Configurar un scheduler ligero en segundo plano (`BackgroundScheduler`) que arranque en el evento `startup` de `main.py`.
   * Tarea periódica programada: Barrido automático cada $N$ minutos (configurable, con modo demostración cada 5 minutos y modo producción cada medianoche).
2. **Algoritmo de Barrido de Acuerdos y Omisiones:**
   * Archivo: `backend/app/services/reunion_service.py`.
   * Función: `ejecutar_barrido_acuerdos_periodico(db: Session)`.
   * Lógica:
     * Si `estado == 'PENDIENTE'` y `fecha_compromiso < hoy`: actualiza a `'ATRASADO'`, calcula `dias_atraso = (hoy - fecha).days` y genera un registro de alerta.
     * Detección de **Omisiones**: Si una tarea lleva $\ge 2$ reuniones del mismo proyecto sin haber sido completada ni mencionada, se marca como `'OMISION'` y se dispara una alerta de riesgo para el Project Manager.
3. **Persistencia de Alertas en Base de Datos:**
   * Archivo: `backend/app/db/models/alerta.py`.
   * Tabla: `alertas_sistema`.
   * Campos: `id`, `proyecto_id`, `acuerdo_id`, `tipo_alerta` (ATRASO, OMISION, SLA_EXCEDIDO, VACA_FAILOVER), `nivel_severidad` (INFO, WARNING, CRITICAL), `mensaje`, `leida`, `creada_en`.
4. **Motor de Notificaciones y Webhooks:**
   * Archivo: `backend/app/services/alert_service.py`.
   * Despacho configurable:
     * Disparo de Webhook HTTP (POST JSON a una URL configurable de Discord, Slack o webhook.site para demostración en vivo).
     * Registro simulador de correo electrónico (guarda el payload de email en logs de auditoría o tabla de notificaciones para no depender obligatoriamente de un servidor SMTP con credenciales de pago).
5. **Endpoints de Consulta y Disparo:**
   * Archivo: `backend/app/api/v1/endpoints/sistema.py`.
   * `GET /api/v1/sistema/alertas`: Lista las alertas activas del sistema.
   * `POST /api/v1/sistema/alertas/{id}/marcar-leida`: Marca la alerta como atendida.
   * `POST /api/v1/sistema/ejecutar-scheduler-manual`: Permite al jurado forzar el barrido periódico de medianoche con un clic en tiempo real.

---

## 📊 FASE 2: MLOPS EN VIVO — DATA DRIFT, CALIBRACIÓN DE WER Y MODEL REGISTRY
> **Brechas cubiertas:** Brecha 3 (Monitoreo de Data Drift y WER en producción) y Brecha 4 (Model Registry / Prompt Tracking).  
> **Estimación de esfuerzo:** 2 días de desarrollo.  
> **Responsable sugerido:** Alejandro Martínez (Modelos, Datos & MLOps).

### 2.1. Contexto y Justificación
El docente insistió en que el combustible del sistema inteligente son los datos y que debe existir una separación clara entre el dataset, el modelo y las métricas. Para superar la brecha de no tener cálculo de WER en tiempo real, se implementará un **Módulo de Calibración Continua y Deriva de Datos**.

### 2.2. Tareas Técnicas Detalladas
1. **Calibrador y Evaluador de WER en Vivo (`eval_service.py`):**
   * Archivo: `backend/app/services/eval_service.py`.
   * Implementar la matriz matemática formal del Segundo Corte:
     $$\text{WER} = \frac{S + D + I}{N}, \quad \text{WER}_w = \frac{\sum (w_k \cdot \text{error}_k)}{\sum w_j}$$
   * Pesos aplicados: Fechas y Negaciones ($3.0$), Nombres propios ($2.0$), Verbos clave ($1.5$), Comunes ($1.0$), Artículos ($0.3$).
   * Endpoint: `POST /api/v1/auditoria/calibrar-wer`.
     * Recibe: Archivo de audio (o ID de reunión ya procesada) + Archivo de texto con el *Ground Truth* manual de referencia.
     * Devuelve: JSON con $\text{WER}$, $\text{WER}_w$, Precisión, Deletion Rate, Substitution Rate, Insertion Rate, Longitud Relativa y lista de palabras sustituidas.
2. **Detector de Data Drift (Deriva del Vocabulario y Calidad):**
   * Archivo: `backend/app/services/eval_service.py`.
   * Función: `analizar_data_drift(transcripcion: str, db: Session)`.
   * Lógica:
     * Mantiene un vocabulario base de referencia (extraído de los primeros audios del proyecto).
     * Para cada nueva reunión, calcula el **Índice de Vocabulario Desconocido (Out-of-Vocabulary Ratio - OOV)** y el porcentaje de términos con bajo nivel de confianza fonética.
     * Si el ratio OOV supera el $15\%$, clasifica la reunión con **Alerta de Data Drift** (indicando que el equipo está usando nueva jerga o que la acústica empeoró).
3. **Registro de Prompts y Versionado de Modelos (Prompt & Model Registry):**
   * Archivo: `backend/app/core/prompt_registry.py`.
   * Versionado de Prompts:
     * `v1_base`: Prompt estándar básico (Intento 3).
     * `v2_informal`: Prompt mejorado para conversaciones tácitas e informales (Intento 4).
     * `v3_hibrido`: Prompt estructurado de doble llamada con resumen ejecutivo (Intento 5).
   * Persistencia en BD: En cada inferencia, se guarda en `auditoria_ia_logs` qué versión exacta de prompt se utilizó y qué hash de modelo de Whisper (`medium`, `small`, `large`) ejecutó la transcripción.
4. **Endpoints de Auditoría MLOps:**
   * Archivo: `backend/app/api/v1/endpoints/auditoria.py`.
   * `POST /api/v1/auditoria/calibrar-wer`: Ejecuta la evaluación contra Ground Truth.
   * `GET /api/v1/auditoria/data-drift`: Devuelve el histórico de deriva de vocabulario de las reuniones.
   * `GET /api/v1/auditoria/prompts-historial`: Lista las versiones de prompts y sus tasas de éxito asociadas.

---

## ⚡ FASE 3: ALTA DISPONIBILIDAD — MODO CONSENSO CONCURRENTE EN VACAS
> **Brechas cubiertas:** Brecha 2 (Consenso Triple en Paralelo vs Fallback Secuencial) y Brecha 7 (Refuerzo de Auditoría del Perceptrón).  
> **Estimación de esfuerzo:** 1 día de desarrollo.  
> **Responsable sugerido:** Daniel Felipe Castro (Backend & Algoritmos).

### 3.1. Contexto y Justificación
En el marco teórico original se propuso que el Perceptrón enviaría en paralelo peticiones a múltiples LLMs para votar por consenso si la discrepancia superaba el $20\%$. Implementaremos este modo como una opción avanzada de auditoría.

### 3.2. Tareas Técnicas Detalladas
1. **Evolución de `VACASManager` con Modo Dual:**
   * Archivo: `backend/app/services/vacas.py`.
   * Añadir el parámetro booleano: `modo_consenso: bool = False`.
2. **Implementación de Concurrencia con `asyncio.gather`:**
   * Si `modo_consenso == False` (Modo Estándar / Económico): Ejecuta en cascada secuencial rápida (DeepSeek $\rightarrow$ OpenAI $\rightarrow$ Offline).
   * Si `modo_consenso == True` (Modo Auditoría / Consenso Activo):
     * Dispara concurrentemente la inferencia hacia **DeepSeek** (`deepseek-chat`) y hacia **OpenAI** (`gpt-4o-mini`).
     * Calcula la distancia de Levenshtein y el ratio de discrepancia léxica entre ambas listas JSON de acuerdos extraídos:
       $$\text{Discrepancia} = 1.0 - \text{Similitud}(JSON_{\text{DeepSeek}}, JSON_{\text{OpenAI}})$$
     * Si $\text{Discrepancia} \le 0.20$ ($20\%$ de tolerancia prometida): Considera que hay **Consenso** y selecciona la respuesta con mayor completitud.
     * Si $\text{Discrepancia} > 0.20$: El Perceptrón clasifica la ejecución como **Nivel 2 (Warning por Discrepancia entre LLMs)**, guarda ambas respuestas en el log y emite alerta para revisión humana.
3. **Parametrización en la API:**
   * Archivo: `backend/app/api/v1/endpoints/reuniones.py`.
   * Añadir el parámetro query: `modo_consenso: bool = Query(False, description="Si es True, ejecuta DeepSeek y OpenAI en paralelo para votar por consenso")`.

---

## 🎨 FASE 4: INTEGRACIÓN EN FRONTEND (ANGULAR 19) Y DEMO DE SUSTENTACIÓN
> **Brechas cubiertas:** Consolidación visual de todas las brechas cerradas en las Fases 1, 2 y 3.  
> **Estimación de esfuerzo:** 1.5 a 2 días de desarrollo.  
> **Responsable sugerido:** Bryan Alexander Betancourt (Frontend & UX).

### 4.1. Contexto y Justificación
El profesor y el jurado evalúan la experiencia de extremo a extremo. Todo lo nuevo construido en el backend debe ser visible, interactivo y demostrable con un clic en la interfaz web de Angular 19.

### 4.2. Tareas Técnicas Detalladas
1. **Centro de Alertas y Notificaciones (Fase 1 en UI):**
   * Archivo: `frontend-angular/src/app/app.component.ts`.
   * Agregar en la barra superior un icono de campana con contador de alertas no leídas (`/api/v1/sistema/alertas`).
   * Panel desplegable o modal que muestra las tareas en riesgo de atraso y las omisiones detectadas por el scheduler de medianoche.
   * Botón: *"Ejecutar barrido nocturno ahora"* para disparar en vivo la Curva de Espacios Iguales ante el jurado.
2. **Pestaña de Calibración MLOps y Benchmark en `/auditoria` (Fase 2 en UI):**
   * Archivo: `frontend-angular/src/app/pages/auditoria.component.ts`.
   * Nueva sección: *"Calibrador de Precisión (WER & Drift)"*.
   * Formulario de subida: Seleccionar reunión existente o audio + Cargar archivo `.txt` con el Ground Truth.
   * Tarjeta de resultados:
     * Visualizador de métricas con barras de progreso: $\text{WER}$ (Meta $<10\%$), $\text{WER}_w$ (Meta $<8\%$), Precisión ($>90\%$), Eliminaciones, Sustituciones e Inserciones.
     * Indicador visual de **Data Drift** (Verde = Vocabulario estable, Amarillo = Deriva moderada).
3. **Controles de Concurrencia y Resiliencia en `/subir` (Fase 3 en UI):**
   * Archivo: `frontend-angular/src/app/pages/subir.component.ts`.
   * Agregar switch interactivo: *"Modo Consenso Dual (DeepSeek + OpenAI)"*.
   * Si está activo, mostrar en la vista de minuta un badge que indique *"Validado por Consenso Dual (Discrepancia < 20%)"*.

---

## 📦 5. MATRIZ DE ASIGNACIÓN DE TAREAS Y ENTREGABLES

| Integrante | Rol Principal | Fases Asignadas | Entregables Concretos |
| :--- | :--- | :--- | :--- |
| **Daniel Castro** | Líder Técnico & Backend | **Fase 1 y Fase 3** | • `scheduler.py` (APScheduler en FastAPI)<br>• `alert_service.py` y endpoints de alertas<br>• Modo Consenso paralelo en `vacas.py`<br>• Pruebas unitarias de integración |
| **Alejandro Martínez** | Ingeniero de IA & MLOps | **Fase 2** | • `eval_service.py` (Cálculo matemático de WER/WERw)<br>• Detector de Data Drift léxico<br>• `prompt_registry.py` con versionado de prompts<br>• Documentación de métricas para el informe |
| **Bryan Betancourt** | Desarrollador Frontend UI/UX | **Fase 4** | • Campana de alertas en barra superior de Angular<br>• Panel visual de Calibración WER en `/auditoria`<br>• Switch de Modo Consenso en `/subir`<br>• Verificación de responsive design y build |

---

## 🏆 RESULTADO TRAS COMPLETAR EL PLAN

Al finalizar estas 4 fases:
1. **La Curva de Espacios Iguales** pasará del **50% al 100%** de cumplimiento con el scheduler de medianoche.
2. **El Sistema de Alertas** pasará del **40% al 100%** con webhooks y centro de notificaciones.
3. **El Monitoreo de MLOps y Data Drift** pasará del **60% al 100%** con el calibrador de WER en vivo.
4. **La Tolerancia a Fallos VACAS** pasará del **75% al 100%** al soportar tanto el modo cascada como el modo consenso concurrente.
5. El proyecto no solo cumplirá con la rúbrica del profesor al 100%, sino que constituirá una plataforma de nivel profesional con arquitectura robusta, auditable y con código limpio.

---

## ✅ ESTADO DE EJECUCIÓN: 100% IMPLEMENTADO Y VERIFICADO (Noviembre 2026)

Todas las 4 fases han sido implementadas, integradas y verificadas con éxito en el monorepositorio (`prototipos`):

1. **Fase 1 (Curva de Espacios Iguales & Alertas):**
   - APScheduler integrado en el ciclo de vida de FastAPI (`app/core/scheduler.py`).
   - Detección de compromisos atrasados y omisiones ($\ge 2$ reuniones sin mencionar).
   - Tabla `alertas_sistema` en PostgreSQL y despacho multicanal (`app/services/alert_service.py`).
   - Endpoints: `GET /sistema/scheduler/estado`, `POST /sistema/scheduler/ejecutar`, `GET /sistema/alertas`, `POST /sistema/alertas/{id}/marcar-leida`.

2. **Fase 2 (MLOps en Vivo: WER, WER Ponderado, Data Drift y Prompt Registry):**
   - Servicio matemático `app/services/eval_service.py` con alineación Levenshtein exacta token por token.
   - Cálculo de $WER$, $WER_w$ (pesos Fechas/Negaciones=3.0, Nombres=2.0, Verbos=1.5), Precisión, $S$, $D$, $I$, $H$ y Longitud Relativa.
   - Detección de Data Drift léxico mediante ratio Out-Of-Vocabulary (OOV) y alertas sobre modismos.
   - Prompt Registry (`app/core/prompt_registry.py`) con versiones versionadas (`v1_base`, `v2_informal`, `v3_hibrido`), hashes MD5 inmutables y activación en caliente.
   - Tabla `evaluaciones_calibracion` persistente en PostgreSQL.

3. **Fase 3 (Alta Disponibilidad: Consenso Dual Concurrente en VACAS):**
   - Ejecución concurrente con `ThreadPoolExecutor` de DeepSeek y OpenAI en `app/services/vacas.py`.
   - Cálculo de discrepancia léxica entre modelos ($\le 20\%$ de tolerancia SLA).
   - Clasificación por Perceptrón: Nivel 0 (Consenso Total) vs Nivel 2 (Warning por Discrepancia Cognitiva).
   - Tolerancia a fallos con fallback automático al modelo sobreviviente o reglas offline.

4. **Fase 4 (Frontend Angular 19 & UX de Demostración):**
   - Barra superior con icono de campana `🔔`, contador dinámico de alertas y drawer interactivo con disparador de la Curva de Espacios Iguales en vivo.
   - Tablero MLOps completo en `/auditoria`:
     - Pestaña de Calibración WER con diff interactivo token a token resaltado por color.
     - Pestaña de Data Drift con medidor OOV y vocabulario detectado.
     - Pestaña de Prompt Registry con tarjetas de versiones y botón para activación en producción.
   - Control de activación de Modo Consenso Dual en `/subir`.
   - Compilación exitosa verificada: `npm run build` sin errores.


