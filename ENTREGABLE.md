# 🎓 Transcriptor Maestro — Documento Oficial de Entregables y Arquitectura
> **Universidad ECCI — Facultad de Ingeniería**  
> **Programa:** Ingeniería de Sistemas  
> **Asignatura / Proyecto:** Inteligencia Artificial / Proyecto de Grado / MLOps Enterprise  
> **Fecha de Entrega:** Noviembre de 2026 — Bogotá D.C., Colombia  
> **Versión del Proyecto:** 3.0.0 (Entrega Final / Corte 3)

---

## 👥 Integrantes del Proyecto

| Nombre Completo | Rol en el Proyecto | Responsabilidades Principales |
| :--- | :--- | :--- |
| **Daniel Felipe Castro** | Arquitecto de Software & Líder Backend / IA | Diseño de arquitectura FastAPI, controladores REST `ResponseDto`, persistencia dual PostgreSQL/SQLite, orquestación del pipeline ASR Whisper y endpoint de cancelación segura. |
| **Alejandro Martínez** | Ingeniero de MLOps, Datos y Resiliencia | Infraestructura de auditoría MLOps, orquestador de contingencia VACAS, Calibrador de WER ponderado, detección de Drift léxico y benchmarking acústico. |
| **Bryan Betancourt** | Scrum Master & Líder Frontend / UX | Dirección metodológica, desarrollo de la interfaz de usuario en Angular (SPA), integración de telemetría MLOps, diseño visual y articulación del guion de sustentación. |

---

## 🔗 Enlace Oficial del Repositorio

El código fuente completo, historial de commits, prototipos y documentación técnica versionada se encuentran alojados en GitHub:

* **Repositorio GitHub:** [https://github.com/FelipeCastro5/transcriptor-maestro](https://github.com/FelipeCastro5/transcriptor-maestro)
* **Rama Principal de Producción:** `main`

---

## 📁 Estructura y Ubicación de los Entregables

Todos los artefactos académicos, técnicos y analíticos generados a lo largo del proyecto se encuentran centralizados dentro de la carpeta `EntregaFinal/`:

```text
EntregaFinal/
├── DOCUMENTO_FINAL_PROYECTO.docx.pdf          # Documento formal consolidado bajo normas APA 7
├── Transcriptor Maestro – Sustentación Final.pptx # Presentación ejecutiva de diapositivas
└── ground-truth/                              # Dossier completo de experimentación y validación
    ├── INFORME_COMPARATIVO_MODELOS_VS_GROUND_TRUTH.md # Informe técnico tripartito (Small vs Medium vs Large)
    ├── RESULTADOS_3_MODELOS_DB.md            # Extracción en bruto de la BD (MEET-441821BF, MEET-7556833C, MEET-18F4FE34)
    ├── new-guion.md                           # Guion oficial de simulación de reunión técnica (>5 min)
    ├── tareas-organizadas.md                  # Matriz de verdad canónica (Ground Truth) de compromisos
    └── linea-de-tiempo.md                     # Cronología de todo el desarrollo del proyecto desde prototipos
```

### 📋 Descripción Detallada de los Entregables:

1. **Documento Técnico Formal:**  
   [`EntregaFinal/DOCUMENTO_FINAL_PROYECTO.docx.pdf`](./EntregaFinal/DOCUMENTO_FINAL_PROYECTO.docx.pdf)  
   Monografía exhaustiva del proyecto con fundamentación teórica, análisis del estado del arte, arquitectura detallada, pruebas empíricas y conclusiones bajo estándares de publicación académica APA 7.

2. **Presentación de Diapositivas para Sustentación:**  
   [`EntregaFinal/Transcriptor Maestro – Sustentación Final (1).pptx`](./EntregaFinal/Transcriptor%20Maestro%20%E2%80%93%20Sustentaci%C3%B3n%20Final%20(1).pptx)  
   Material visual de apoyo para la sustentación ante el jurado, estructurado en torno a la problemática, diseño de arquitectura, resiliencia MLOps, resultados comparativos y demostración en vivo.

3. **Informe Comparativo de Modelos vs. Ground Truth:**  
   [`EntregaFinal/ground-truth/INFORME_COMPARATIVO_MODELOS_VS_GROUND_TRUTH.md`](./EntregaFinal/ground-truth/INFORME_COMPARATIVO_MODELOS_VS_GROUND_TRUTH.md)  
   Estudio comparativo riguroso que contrasta el desempeño de **Whisper Small**, **Whisper Medium** y **Whisper Large** contra el audio patrón de 6 min 38 s. Incluye matrices de confusión, Real Time Factor ($RTF$), análisis de degradación fonética en jerga técnica, evaluación del algoritmo de *Fuzzy Matching* ($S_{fuzzy} \ge 0.75$) y la demostración empírica de **Whisper Medium como el Punto Dulce (*Sweet Spot*)** operativo.

4. **Registros de Base de Datos de las Pruebas:**  
   [`EntregaFinal/ground-truth/RESULTADOS_3_MODELOS_DB.md`](./EntregaFinal/ground-truth/RESULTADOS_3_MODELOS_DB.md)  
   Extracción íntegra y transparente desde PostgreSQL (`transcriptor_db`) para los tres identificadores evaluados:
   * `MEET-441821BF`: Whisper Small (444.38 s cómputo | 9 acuerdos extraídos).
   * `MEET-7556833C`: Whisper Medium (1,428.21 s cómputo | 10 acuerdos extraídos).
   * `MEET-18F4FE34`: Whisper Large (3,098.01 s cómputo | 7 acuerdos extraídos).  
   Incluye metadatos JSON completos, transcripciones acústicas, resúmenes ejecutivos, acuerdos y logs de auditoría IA.

5. **Guion de Simulación Técnica (Audio Patrón):**  
   [`EntregaFinal/ground-truth/new-guion.md`](./EntregaFinal/ground-truth/new-guion.md)  
   Transcripción canónica de la reunión de sincronización del equipo de 5 minutos y 15 segundos (~1,103 palabras habladas, 21 turnos), diseñada intencionalmente con jerga de ingeniería y apodos para someter a estrés el sistema.

6. **Matriz de Compromisos Canónicos (Ground Truth):**  
   [`EntregaFinal/ground-truth/tareas-organizadas.md`](./EntregaFinal/ground-truth/tareas-organizadas.md)  
   Patrón de oro con la especificación de los 3 compromisos operativos obligatorios de cierre (Alejo / MLOps en Angular, Felipe / Cancelación y APA 7, Bryan / Guion y Diapositivas), fechas límites y cierres técnicos previos.

7. **Línea de Tiempo del Proyecto:**  
   [`EntregaFinal/ground-truth/linea-de-tiempo.md`](./EntregaFinal/ground-truth/linea-de-tiempo.md)  
   Registro cronológico detallado de la evolución del proyecto a lo largo del semestre académico: desde la conceptualización de los 5 prototipos en Python hasta la arquitectura empresarial completa desplegada en local.

---

## 🏛️ Explicación de la Arquitectura del Sistema (`prototipos/`)

El sistema **Transcriptor Maestro** adopta una arquitectura desacoplada por capas basada en microservicios modulares, integrando principios de **MLOps**, **resiliencia con conmutación en caliente (*Hot Failover*)** y diseño centrado en el usuario.

### 📐 Diagrama Arquitectónico Global

```mermaid
flowchart TD
    subgraph Frontend["Frontend SPA (Angular 19)"]
        UI_Upload["Subir Reunión (Audio / Texto)"]
        UI_History["Historial & Eliminación en Cascada"]
        UI_Minuta["Minuta Detallada + Pestaña Metadata"]
        UI_MLOps["Panel Auditoría MLOps (VACAS / WER / Drift / Prompts)"]
    end

    subgraph Backend["Backend API (FastAPI / Python 3.11+)"]
        REST_Ctrl["Controladores REST (ResponseDto)"]
        Service_Reun["Servicio de Reuniones & Cancelación"]
        Service_ASR["Pipeline ASR (Whisper con Chunking 30s)"]
        Service_Orq["Orquestador VACAS & Perceptrón"]
        Service_Fuzzy["Motor Fuzzy Matching (Levenshtein >= 0.75)"]
    end

    subgraph AI_Providers["Proveedores de IA"]
        LLM_DeepSeek["DeepSeek Chat (Proveedor Primario)"]
        LLM_OpenAI["OpenAI GPT-4o-mini (Réplica Failover)"]
        Whisper_Local["OpenAI Whisper Local (Small / Medium / Large)"]
    end

    subgraph Storage["Capa de Persistencia Dual"]
        DB_PG[("PostgreSQL (transcriptor_db)")]
        DB_SQLite[("SQLite Fallback (local_fallback.db)")]
        Storage_Temp["Almacenamiento Temporal de Audio"]
    end

    UI_Upload -->|POST /api/v1/reuniones/procesar| REST_Ctrl
    UI_History -->|GET / DELETE (Cascada)| REST_Ctrl
    UI_Minuta -->|GET /api/v1/reuniones/:id| REST_Ctrl
    UI_MLOps -->|GET /api/v1/auditoria| REST_Ctrl

    REST_Ctrl --> Service_Reun
    Service_Reun --> Service_ASR
    Service_ASR --> Whisper_Local
    Service_Reun --> Service_Orq
    Service_Orq -->|Primario| LLM_DeepSeek
    Service_Orq -.->|Hot Failover < 3s| LLM_OpenAI
    Service_Orq --> Service_Fuzzy

    REST_Ctrl --> DB_PG
    DB_PG -.->|Fallo de Conexión| DB_SQLite
    Service_ASR --> Storage_Temp
```

### 🧩 Componentes Principales

1. **Frontend en Angular 19 (`frontend-angular/`):**
   * **Diseño Dark Enterprise:** Desarrollado con Tailwind CSS y componentes reactivos.
   * **Vistas Especializadas:**
     * *Subir Reunión:* Carga de audios (`.mp3`, `.wav`, `.m4a`) o texto crudo con selección de estrategia (1 a 5) y modelo Whisper (`small`, `medium`, `large`).
     * *Historial de Reuniones:* Listado interactivo con estados (`COMPLETADO`, `CANCELADO`, `ERROR`) y botón de **eliminación segura en cascada**.
     * *Vista Minuta:* Presentación ejecutiva con resumen, acuerdos organizados por integrante y **pestaña exclusiva de Metadatos Técnicos** (tiempos exactos de ASR/LLM, configuración de prompts y hashes MD5).
     * *Panel de Auditoría MLOps:* Cuatro sub-pestañas operativas: Telemetría del orquestador VACAS con simulación de fallos (*Chaos Testing*), Calibrador de WER ponderado en tiempo real, Monitor de deriva léxica (*Data Drift*) y Registro versionado de prompts.

2. **Backend API en FastAPI (`backend/`):**
   * **Estándar Empresarial `ResponseDto<T>`:** Todas las respuestas REST encapsulan de manera estricta la estructura `{ "code": 200, "message": "...", "data": { ... } }`.
   * **Cancelación Asíncrona Segura:** Endpoint dedicado `DELETE /api/v1/reuniones/{id}` que frena el procesamiento en segundo plano, libera memoria RAM y purga los archivos temporales de almacenamiento.
   * **Persistencia Dual con Fallback Transparente:** Conexión nativa a **PostgreSQL** mediante `pg8000`. Si el motor relacional no responde, el sistema conmuta automáticamente a **SQLite** en local, impidiendo la caída del servicio.

3. **Orquestador de Resiliencia VACAS & Perceptrón:**
   * **Mecanismo de Hot Failover:** Monitorea activamente la latencia y disponibilidad de la API de DeepSeek. Ante fallos de conexión o cuota agotada, conmuta a la réplica de OpenAI en menos de 3 segundos sin interrumpir al usuario.
   * **Modo Consenso Dual:** Capacidad de consultar dos modelos en paralelo mediante `ThreadPoolExecutor`, midiendo discrepancias léxicas y alertando si difieren en más del 20%.

4. **Algoritmo de Identidad (*Fuzzy Matching*):**
   * Emplea distancia de Levenshtein normalizada sobre el catálogo de integrantes de PostgreSQL.
   * Resuelve eficazmente apodos informales (*"Alejo"* $\to$ Alejandro Martínez al 95%, *"Felipe"* $\to$ Daniel Castro al 95%, *"Brian"* $\to$ Bryan Betancourt al 80%). Si el interlocutor es difuso, activa el fallback institucional `Equipo General` ($S_{fuzzy} = 0.286$).

---

## 🛠️ Tutorial Completo de Instalación y Puesta en Marcha

Sigue estas instrucciones detalladas para clonar, configurar y ejecutar la solución en un entorno local:

### 1. Prerrequisitos del Sistema

Asegúrate de contar con las siguientes herramientas instaladas:
* **Python 3.10 o superior** (3.11 / 3.14 compatible).
* **Node.js 18.x o 20.x LTS** y **npm 9.x+**.
* **PostgreSQL 14 o superior** (Opcional: el sistema incluye fallback automático a SQLite si PostgreSQL no está disponible).
* **FFmpeg** configurado en las variables de entorno (`PATH`) para decodificación de audio.
* **Git**.

---

### 2. Clonación del Repositorio

Abre una terminal (PowerShell en Windows o Bash en Linux/macOS) y clona el repositorio:

```bash
git clone https://github.com/FelipeCastro5/transcriptor-maestro.git
cd transcriptor-maestro
```

---

### 3. Configuración y Despliegue del Backend (FastAPI)

1. Ingresa a la carpeta del backend:
   ```bash
   cd backend
   ```

2. Crea y activa el entorno virtual de Python:
   * **En Windows (PowerShell):**
     ```powershell
     python -m venv venv
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
     .\venv\Scripts\Activate.ps1
     ```
   * **En Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instala las dependencias del proyecto:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configura el archivo de variables de entorno `.env`:
   Crea o verifica el archivo `.env` en `backend/` con los siguientes parámetros:
   ```env
   PROJECT_NAME="Transcriptor Maestro API"
   API_V1_STR="/api/v1"
   ENVIRONMENT="development"
   DEBUG=True

   UPLOAD_DIR="storage/audios_temp"
   OUTPUT_DIR="storage/salidas"

   # Conexión a PostgreSQL (Usuario y contraseña configurados en tu motor)
   DATABASE_URL="postgresql+pg8000://postgres:felipe@localhost:5432/transcriptor_db"

   # Llaves de API para LLMs
   DEEPSEEK_API_KEY="tu_clave_de_deepseek"
   OPENAI_API_KEY="tu_clave_de_openai_opcional"
   HUGGINGFACE_API_KEY="tu_clave_de_huggingface_opcional"
   ```
   > **Nota de Resiliencia:** Si no dispones de un servidor PostgreSQL activo, puedes omitir `DATABASE_URL` o dejar que el sistema active automáticamente el fallback a SQLite en `storage/local_fallback.db`.

5. Ejecuta el servidor Backend:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * **API en línea:** `http://localhost:8000`
   * **Documentación Interactiva Swagger UI:** `http://localhost:8000/docs`

---

### 4. Configuración y Despliegue del Frontend (Angular 19)

1. Abre una **segunda terminal** y navega a la carpeta del frontend:
   ```bash
   cd frontend-angular
   ```

2. Instala los paquetes de Node:
   ```bash
   npm install
   ```

3. Inicia el servidor de desarrollo de Angular:
   ```bash
   npm start
   # o alternativamente:
   npx ng serve --port 4200
   ```

4. Abre tu navegador web e ingresa a:
   👉 **`http://localhost:4200`**

---

### 5. Verificación de Funcionamiento (Prueba Rápida)

1. **Dashboard Principal:** Al entrar a `http://localhost:4200`, verifica que el indicador de estado en la barra superior señale **"API en línea"**.
2. **Subida de Prueba:** Ve a la pestaña **Subir Reunión**, selecciona un archivo de audio o pega un texto de prueba, selecciona **Estrategia 5 (Híbrido VACAS)** y haz clic en **Procesar Reunión**.
3. **Consulta de Minuta y Metadatos:** Al finalizar, el sistema te redirigirá a la minuta donde podrás revisar el resumen ejecutivo, los compromisos asignados por Fuzzy Matching y la pestaña **Metadata** con la auditoría completa de cómputo.
4. **Auditoría MLOps:** Navega al menú **Auditoría MLOps** para explorar las métricas de telemetría, el calibrador WER y el botón de simulación de contingencia VACAS.

---

## 🎯 Conclusión del Proyecto

**Transcriptor Maestro** demuestra que la combinación de modelos acústicos optimizados (**Whisper Medium** como estándar de equilibrio cómputo-precisión), arquitecturas de resiliencia ante caídas de proveedores de IA (**VACAS**) y algoritmos de resolución de entidades mediante *Fuzzy Matching* permite construir una herramienta robusta, confiable y con aplicación inmediata en entornos corporativos reales.

Todos los artefactos probatorios, código fuente y análisis comparativos quedan formalmente radicados y a entera disposición del jurado evaluador.
