# 🎙️ Transcriptor Maestro

> **Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos**  
> Prototipo empresarial para la transcripción automática de reuniones, extracción estructurada de acuerdos mediante Inteligencia Artificial y gestión operativa de compromisos.

---

## 📖 ¿Qué es este proyecto?

**Transcriptor Maestro** es una plataforma diseñada para resolver uno de los mayores problemas en la gestión de proyectos: la pérdida de acuerdos y compromisos verbales tomados durante reuniones de trabajo.

El sistema permite subir grabaciones de audio de reuniones, transcribirlas automáticamente, generar resúmenes ejecutivos y extraer compromisos clave asignándolos a los miembros del equipo mediante procesamiento de lenguaje natural y algoritmos de coincidencia difusa (*Fuzzy Matching*).

### 🌟 Capacidades Clave

1. **Transcripción Automatizada de Audio:** Procesa archivos de audio en segundo plano usando modelos de IA (HuggingFace / Whisper).
2. **Extracción Inteligente de Acuerdos:** Utiliza LLMs avanzados (DeepSeek / OpenAI) para identificar tareas, fechas de compromiso, contexto original y responsables directos.
3. **Resolución de Nombres (*Fuzzy Matching*):** Mapea variaciones coloquiales y apodos hablados (ej. *"Juancho"*, *"Mary"*) al responsable formal correspondiente en la base de datos.
4. **Alta Resiliencia y Contingencia (*VACAS* & *El Perceptrón*):** Mecanismo de respaldo (*Hot Failover*) que conmuta automáticamente entre proveedores de IA en caso de latencia o fallos de servicio.
5. **API REST Estandarizada:** Todas las respuestas del backend siguen estrictamente el patrón empresarial `ResponseDto<T>` (`{ "code", "message", "data" }`).

---

## 📚 Guías de Configuración y Despliegue

Para poner en marcha el proyecto paso a paso, consulta las guías dedicadas:

| Componente | Documento | Descripción |
| :--- | :--- | :--- |
| **Cierre de Promesas MLOps** | 🏆 [**`CAMBIOS_PLAN_CIERRE_PROMESAS.md`**](./CAMBIOS_PLAN_CIERRE_PROMESAS.md) | **Informe de cumplimiento 100%:** Curva de Espacios Iguales, Alertas, Calibrador WER, Data Drift, Prompt Registry y Modo Consenso VACAS. |
| **Backend** | 👉 [**`backend/GUIA_INICIO_BACKEND.md`**](./backend/GUIA_INICIO_BACKEND.md) | **Paso a paso para principiantes:** instalación de dependencias, entorno virtual, encendido del servidor con Uvicorn y prueba de endpoints en Swagger. |
| **Base de Datos** | 👉 [**`db/README.md`**](./db/README.md) | **Guía de carga de base de datos:** cómo crear la base de datos `transcriptor_db` y cargar [`db.sql`](./db/db.sql) con pgAdmin 4 o terminal `psql`. |
| **Arquitectura** | 📄 [**`backend/doc.md`**](./backend/doc.md) | Explicación detallada de la arquitectura por capas (controladores, servicios, modelos y IA). |
| **Frontend Handoff** | 📄 [**`backend/FRONTEND_HANDOFF.md`**](./backend/FRONTEND_HANDOFF.md) | Especificación técnica de contratos JSON, endpoints y flujos para el equipo de desarrollo Frontend. |
| **Frontend (Angular)** | 👉 [**`frontend-angular/README.md`**](./frontend-angular/README.md) | Interfaz web Angular 19: subida de audios, minutas, historial, Kanban de acuerdos, equipo y auditoría. |
| **Frontend (React)** | 👉 [**`frontend/README.md`**](./frontend/README.md) | Misma interfaz en React + Vite (alternativa). |

---

## 📂 Estructura del Repositorio

```text
prototipos/
├── README.md                      # Este documento (Visión general del proyecto)
├── db/
│   ├── README.md                  # 🗄️ Guía completa de instalación y carga de BD
│   └── db.sql                     # Script SQL con tablas, extensión UUID e índices
└── backend/
    ├── GUIA_INICIO_BACKEND.md     # 🚀 Guía paso a paso para iniciar el backend
    ├── README.md                  # Referencia rápida de endpoints y comandos
    ├── doc.md                     # Documentación técnica de arquitectura
    ├── FRONTEND_HANDOFF.md        # Guía de integración para desarrolladores Frontend
    ├── requirements.txt           # Lista de dependencias de Python
    ├── .env                       # Variables de entorno y credenciales locales
    ├── app/
    │   ├── main.py                # Punto de entrada de FastAPI y configuración CORS
    │   ├── api/v1/                # Enrutadores y controladores REST (reuniones, acuerdos, etc.)
    │   ├── core/                  # Configuraciones globales y lógica de resiliencia
    │   ├── db/                    # Modelos SQLAlchemy y conexión a BD (con fallback a SQLite)
    │   ├── schemas/               # Esquemas Pydantic y ResponseDto
    │   └── services/              # Lógica de negocio, IA Handler, VACAS y Fuzzy Matching
    ├── scripts/
    │   ├── init_db.py             # Script utilitario para verificar/crear la BD en PostgreSQL
    │   └── clean_storage.py       # Script para limpieza de audios y archivos temporales
    └── storage/                   # Almacenamiento local temporal de audios y salidas
```

---

## ▶️ Cómo arrancar el proyecto (Backend + Frontend)

Necesitas **2 terminales de PowerShell** abiertas en la carpeta raíz del proyecto (`transcriptor-maestro`).
La base de datos **no hay que encenderla**: el servicio de PostgreSQL arranca solo con Windows.

### Terminal 1 — Backend (FastAPI, puerto 8000)

```powershell
cd backend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
py -m uvicorn app.main:app --reload --port 8000
```

Si todo está bien verás:

```text
[DB] Conectado exitosamente a: localhost:5432/transcriptor_db
INFO:     Application startup complete.
```

* Swagger (probar la API): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Salud del servicio: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Terminal 2 — Frontend Angular (puerto 4200)

```powershell
cd frontend-angular
npm start
```

`npm start` instala las dependencias automáticamente (`npm install`) y luego enciende Angular.
Abre 👉 [http://localhost:4200](http://localhost:4200)

*(Alternativa React: `cd frontend; npm install; npm run dev` → [http://localhost:5173](http://localhost:5173)).*

### Apagar

En cada terminal presiona `Ctrl + C`.

### Problemas comunes al arrancar

| Error | Causa | Solución |
| :--- | :--- | :--- |
| `[WinError 10013] An attempt was made to access a socket...` | El puerto 8000 ya está ocupado (otro backend sigue encendido). | Cierra la otra terminal/proceso, o usa otro puerto: `--port 8001` y cambia `8000` por `8001` en [`frontend-angular/proxy.conf.json`](./frontend-angular/proxy.conf.json). |
| `La ejecución de scripts está deshabilitada en este sistema` | Política de PowerShell. | Ejecuta `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` antes de activar el `venv`. |
| `[DB-FALLBACK] ... Usando SQLite local` | PostgreSQL apagado o credenciales distintas. | Verifica el servicio `postgresql-x64-16` y la `DATABASE_URL` de `backend/.env`. |
| El front dice **"API desconectada"** | El backend no está encendido. | Arranca primero la Terminal 1. |

---

## 🧰 Instalación por primera vez (solo una vez)

Si clonas el proyecto en un equipo nuevo, antes de arrancarlo:

1. **Base de datos:** instala PostgreSQL (usuario `postgres`, contraseña `felipe`), crea `transcriptor_db` y carga [`db/db.sql`](./db/db.sql) (ver [Guía de BD](./db/README.md)).
2. **Backend:**
   ```powershell
   cd backend
   py -m venv venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env   # y ajusta DATABASE_URL y las API keys
   py scripts/init_db.py         # crea transcriptor_db si no existe
   ```
3. **Frontend:** no requiere pasos extra; `npm start` instala todo la primera vez.
