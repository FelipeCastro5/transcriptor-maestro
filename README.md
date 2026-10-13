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
| **Backend** | 👉 [**`backend/GUIA_INICIO_BACKEND.md`**](./backend/GUIA_INICIO_BACKEND.md) | **Paso a paso para principiantes:** instalación de dependencias, entorno virtual, encendido del servidor con Uvicorn y prueba de endpoints en Swagger. |
| **Base de Datos** | 👉 [**`db/README.md`**](./db/README.md) | **Guía de carga de base de datos:** cómo crear la base de datos `transcriptor_db` y cargar [`db.sql`](./db/db.sql) con pgAdmin 4 o terminal `psql`. |
| **Arquitectura** | 📄 [**`backend/doc.md`**](./backend/doc.md) | Explicación detallada de la arquitectura por capas (controladores, servicios, modelos y IA). |
| **Frontend Handoff** | 📄 [**`backend/FRONTEND_HANDOFF.md`**](./backend/FRONTEND_HANDOFF.md) | Especificación técnica de contratos JSON, endpoints y flujos para el equipo de desarrollo Frontend. |

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

## ⚡ Inicio Rápido (3 Pasos)

Si ya tienes las herramientas configuradas:

1. **Cargar la base de datos:**  
   Ejecuta [`db/db.sql`](./db/db.sql) en PostgreSQL (revisar [Guía de BD](./db/README.md)).
2. **Instalar dependencias del backend:**  
   ```powershell
   cd backend
   py -m pip install -r requirements.txt
   ```
3. **Encender la API:**  
   ```powershell
   py -m uvicorn app.main:app --reload --port 8000
   ```
4. **Probar la API:**  
   Abre en tu navegador [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
