# 🎙️ Transcriptor Maestro

> **Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos**  
> Prototipo empresarial para la transcripción automática de reuniones, extracción estructurada de acuerdos mediante Inteligencia Artificial y gestión operativa de compromisos.

---

## 📖 ¿Qué es este proyecto?

**Transcriptor Maestro** es una plataforma diseñada para resolver uno de los mayores problemas en la gestión de proyectos: la pérdida de acuerdos y compromisos verbales tomados durante reuniones de trabajo.

El sistema permite subir grabaciones de audio de reuniones, transcribirlas automáticamente, generar resúmenes ejecutivos y extraer compromisos clave asignándolos a los miembros del equipo mediante procesamiento de lenguaje natural y algoritmos de coincidencia difusa (*Fuzzy Matching*).

### 🌟 Capacidades Clave

1. **Transcripción Automatizada de Audio:** Procesa archivos de audio (`.mp3`, `.wav`, `.m4a`, etc.) o minutas en texto usando modelos Whisper (Hugging Face / OpenAI).
2. **Extracción Inteligente de Acuerdos:** Utiliza LLMs avanzados (DeepSeek / OpenAI) o un motor offline por reglas para identificar tareas, fechas de compromiso, contexto original y responsables directos.
3. **Resolución de Nombres (*Fuzzy Matching*):** Mapea variaciones coloquiales y apodos hablados (ej. *"Juancho"*, *"Mary"*) al responsable formal correspondiente en la base de datos con puntaje de similitud ponderado.
4. **Alta Resiliencia y Contingencia (*VACAS* & *El Perceptrón*):** Mecanismo de respaldo (*Hot Failover*) que conmuta automáticamente entre proveedores de IA en caso de latencia, agotamiento de cuota o fallos de servicio.
5. **API REST Estandarizada:** Todas las respuestas del backend siguen estrictamente el patrón empresarial `ResponseDto<T>` (`{ "code", "message", "data" }`).

---

## 📋 Prerrequisitos del Sistema

Antes de iniciar la instalación, asegúrate de contar con los siguientes componentes en tu máquina:

| Herramienta | Versión Recomendada | Propósito |
| :--- | :--- | :--- |
| **Python** | 3.10 o superior (3.11 recomendado) | Runtime del Backend y servicios de IA |
| **Node.js** | 18.x o 20.x LTS | Runtime y compilador del Frontend Angular |
| **npm** | 9.x o superior | Gestor de paquetes de Frontend |
| **PostgreSQL** | 15.x o 16.x *(Opcional)* | Base de datos relacional principal (incluye fallback automático a SQLite) |
| **Git** | 2.x | Control de versiones |
| **FFmpeg** | Cualquier versión reciente *(Opcional/Recomendado)* | Procesamiento y decodificación de formatos de audio en Whisper |

---

## 📚 Documentación Técnica Interna

Para consultar detalles de bajo nivel o guías de referencia por módulo:

| Componente | Documento | Descripción |
| :--- | :--- | :--- |
| **Backend** | 👉 [**`backend/GUIA_INICIO_BACKEND.md`**](./backend/GUIA_INICIO_BACKEND.md) | Guía detallada paso a paso para desplegar y probar la API en FastAPI. |
| **Base de Datos** | 👉 [**`db/README.md`**](./db/README.md) | Guía de creación y carga del esquema `transcriptor_db` mediante pgAdmin o `psql`. |
| **Arquitectura** | 📄 [**`backend/doc.md`**](./backend/doc.md) | Explicación detallada de arquitectura por capas (controladores, servicios, modelos e IA). |
| **Frontend Handoff** | 📄 [**`backend/FRONTEND_HANDOFF.md`**](./backend/FRONTEND_HANDOFF.md) | Especificación de contratos JSON, endpoints y flujos de integración UI. |
| **Frontend Angular** | 👉 [**`frontend-angular/README.md`**](./frontend-angular/README.md) | Documentación de la SPA Angular 19 (rutas, componentes y directivas). |

---

## 🛠️ Instalación y Configuración Inicial (Paso a Paso)

Sigue estos pasos la primera vez que clones o configures el repositorio:

### 1. Clonar el repositorio

```bash
git clone https://github.com/FelipeCastro5/transcriptor-maestro.git
cd transcriptor-maestro
```

---

### 2. Configurar el Backend (Python + FastAPI)

Navega a la carpeta `backend`:

```powershell
cd backend
```

#### A. Crear el Entorno Virtual (`venv`)

- **En Windows (PowerShell):**
  ```powershell
  py -m venv venv
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\venv\Scripts\Activate.ps1
  ```
- **En Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

*(Sabrás que está activo porque tu terminal mostrará el prefijo `(venv)`).*

#### B. Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### C. Crear y Configurar el Archivo de Entorno (`.env`)

Copia la plantilla `.env.example` para generar tu archivo `.env`:

- **Windows:**
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / macOS:**
  ```bash
  cp .env.example .env
  ```

Abre `.env` en tu editor de código y configura las variables:

```ini
PROJECT_NAME="Transcriptor Maestro API"
API_V1_STR="/api/v1"
ENVIRONMENT="development"
DEBUG=True

# Rutas de Almacenamiento local
UPLOAD_DIR="storage/audios_temp"
OUTPUT_DIR="storage/salidas"

# Base de Datos:
# Opción 1 (PostgreSQL local):
DATABASE_URL="postgresql+pg8000://postgres:tu_password@localhost:5432/transcriptor_db"
# Opción 2 (SQLite local - si no deseas instalar PostgreSQL):
# DATABASE_URL="sqlite:///./transcriptor.db"

# Claves de APIs de Inteligencia Artificial (opcionales para modo offline):
DEEPSEEK_API_KEY="tu-deepseek-api-key"
HUGGINGFACE_API_KEY="tu-huggingface-api-key"
OPENAI_API_KEY="tu-openai-api-key"
```

> **Nota sobre el modo sin API Keys:**  
> Si no cuentas con claves de OpenAI o DeepSeek, el sistema cuenta con un motor offline de reglas heurísticas y expresiones regulares que extrae acuerdos y responsables sin costo ni conexión externa.

---

### 3. Configurar la Base de Datos

Tienes dos alternativas según tu conveniencia:

#### Opción A: PostgreSQL (Recomendado para producción/evaluación)
1. Verifica que el servicio de PostgreSQL esté encendido.
2. Ejecuta el script de verificación y creación:
   ```powershell
   py scripts/init_db.py
   ```
3. Ejecuta el script SQL [`db/db.sql`](./db/db.sql) desde pgAdmin 4 o terminal `psql` para poblar el catálogo de integrantes y tablas base.

#### Opción B: SQLite Automático (Zero-Config)
Si no tienes PostgreSQL o prefieres no configurarlo, el backend detecta automáticamente la ausencia de PostgreSQL y conmuta a un archivo SQLite local (`transcriptor.db`), creando las tablas necesarias al arrancar.

---

### 4. Configurar el Frontend (Angular 19)

Abre una **segunda terminal** y navega a la carpeta `frontend-angular`:

```powershell
cd frontend-angular
npm install
```

---

## ▶️ Ejecución del Proyecto

Para trabajar con la plataforma necesitas mantener **2 terminales activas**:

### Terminal 1 — Backend (FastAPI en Puerto 8000)

```powershell
cd backend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
py -m uvicorn app.main:app --reload --port 8000
```

Salida esperada:
```text
[DB] Conectado exitosamente a: localhost:5432/transcriptor_db
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

- **Documentación Interactiva (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Terminal 2 — Frontend (Angular en Puerto 4200)

```powershell
cd frontend-angular
npm start
```

Abre tu navegador en:
👉 [**http://localhost:4200**](http://localhost:4200)

> El frontend utiliza un proxy inverso (`proxy.conf.json`) que redirige automáticamente las peticiones de `/api` y `/health` al backend en el puerto `8000`, evitando problemas de CORS en desarrollo.

---

## 📂 Estructura del Repositorio

```text
prototipos/
├── README.md                      # Documentación maestra del repositorio
├── db/
│   ├── README.md                  # Guía de carga y configuración en PostgreSQL
│   └── db.sql                     # Script DDL con tablas, extensión uuid-ossp e índices
├── backend/
│   ├── GUIA_INICIO_BACKEND.md     # Guía detallada para el desarrollador backend
│   ├── README.md                  # Referencia rápida de comandos de backend
│   ├── doc.md                     # Arquitectura técnica y patrones de diseño
│   ├── FRONTEND_HANDOFF.md        # Especificación técnica de contratos JSON y API REST
│   ├── requirements.txt           # Dependencias de Python (FastAPI, SQLAlchemy, etc.)
│   ├── .env.example               # Plantilla de variables de entorno
│   ├── app/
│   │   ├── main.py                # Punto de entrada de FastAPI y middlewares
│   │   ├── api/v1/                # Controladores REST (reuniones, acuerdos, auditoría)
│   │   ├── core/                  # Configuraciones, prompts y lógica de resiliencia
│   │   ├── db/                    # Sesión SQLAlchemy y conexión resiliente
│   │   ├── schemas/               # Modelos Pydantic y ResponseDto<T>
│   │   └── services/              # IA Handler, conmutación VACAS y Fuzzy Matching
│   ├── scripts/
│   │   ├── init_db.py             # Verificación y creación de base de datos
│   │   └── clean_storage.py       # Limpieza de archivos temporales
│   └── storage/                   # Almacenamiento local temporal de audios
├── frontend-angular/
│   ├── README.md                  # Guía de componentes y arquitectura Angular
│   ├── package.json               # Dependencias de Node (Angular 19, Lucide, Tailwind)
│   ├── proxy.conf.json            # Redirección proxy hacia el backend FastAPI
│   └── src/app/
│       ├── core/                  # Servicios HTTP y modelos TypeScript
│       ├── shared/                # Componentes reutilizables (tablas, badges)
│       └── pages/                 # Vistas: Subir, Minuta, Historial, Acuerdos, Equipo, Auditoría
└── EntregaFinal/
    ├── DOCUMENTO_FINAL_PROYECTO.docx.pdf  # Informe académico y técnico formal
    └── Transcriptor Maestro – Sustentación Final (1).pptx # Presentación de sustentación
```

---

## ⚡ Solución de Problemas Frecuentes

| Síntoma / Error | Causa Raíz | Solución Rápida |
| :--- | :--- | :--- |
| `[WinError 10013] An attempt was made to access a socket...` | El puerto `8000` está ocupado por otro proceso previo. | Detén el proceso anterior o inicia Uvicorn en otro puerto: `--port 8001` y actualiza `target` en `frontend-angular/proxy.conf.json`. |
| `La ejecución de scripts está deshabilitada en este sistema` | Directiva de seguridad de PowerShell en Windows. | Ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de correr `Activate.ps1`. |
| `[DB-FALLBACK] Falló PostgreSQL... Usando SQLite local` | El motor PostgreSQL no está encendido o las credenciales no coinciden. | El sistema seguirá funcionando automáticamente con SQLite. Si requieres PostgreSQL, revisa el servicio de Windows `postgresql-x64-16` y la contraseña en `.env`. |
| En el Frontend aparece **"API Desconectada"** | El backend no está encendido o falló en el arranque. | Inicia la Terminal 1 (Backend) y verifica que responda en `http://127.0.0.1:8000/health`. |
| Error `ModuleNotFoundError` en el backend | Las dependencias no se instalaron en el entorno virtual activo. | Asegúrate de ver `(venv)` en tu consola y vuelve a correr `pip install -r requirements.txt`. |

---

## 📄 Licencia y Créditos

Proyecto desarrollado como parte de la entrega académica de Ingeniería de Sistemas - **Universidad ECCI**.
- **Autor:** Felipe Castro
- **Tecnologías:** FastAPI, Angular 19, PostgreSQL, Whisper, Hugging Face, OpenAI, DeepSeek, RapidFuzz.
