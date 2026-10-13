# 🚀 Guía Paso a Paso: Iniciar el Backend desde Cero

Esta guía está diseñada para que cualquier persona, incluso sin experiencia previa montando APIs en Python, pueda levantar y probar el backend de **Transcriptor Maestro** en su entorno local (Windows).

---

## 📋 Prerrequisitos Básicos

Antes de comenzar, asegúrate de tener instalado en tu computadora:
1. **Python 3.10 o superior** (puedes verificarlo en PowerShell ejecutando `py --version`).
2. **PostgreSQL** (opcional para pruebas iniciales, ya que el sistema cuenta con respaldo automático a SQLite si Postgres no está encendido).

---

## 🛠️ Paso a Paso: Configuración y Despliegue

### Paso 1: Abrir la terminal en la carpeta del backend
Abre **PowerShell** o tu terminal integrada en el editor y navega hasta la carpeta `backend`:
```powershell
cd "c:\MisProyectos\ECCI\trasncriptor maestro\prototipos\backend"
```

---

### Paso 2: Crear y activar un Entorno Virtual (Recomendado)
Un entorno virtual es una carpeta aislada donde se instalan las librerías exclusivas de este proyecto sin alterar el sistema operativo ni otros proyectos.

1. **Crear el entorno virtual:**
   ```powershell
   py -m venv venv
   ```
   *(Esto creará una carpeta llamada `venv` dentro de `backend`)*.

2. **Permitir ejecución de scripts en PowerShell (si no lo has hecho antes):**
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. **Activar el entorno virtual:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(Sabrás que está activo porque aparecerá `(venv)` al inicio de tu línea de comandos)*.

---

### Paso 3: Instalar las dependencias del proyecto
Con el entorno virtual activo, instala todas las librerías listadas en `requirements.txt`:

```powershell
pip install -r requirements.txt
```

> **Alternativa sin entorno virtual:**  
> Si prefieres no usar el entorno virtual, puedes instalar directamente con el lanzador de Python en Windows:
> ```powershell
> py -m pip install -r requirements.txt
> ```

*¿Qué se instala aquí?*
* **FastAPI:** El framework web que gestiona los endpoints y rutas.
* **Uvicorn:** El servidor web ASGI de alto rendimiento.
* **SQLAlchemy & pg8000:** Conexión y manejo de base de datos relacional.
* **Transformers, Torch, SoundFile:** Modelos de Inteligencia Artificial para transcripción de audio.
* **Pydantic:** Validación estricta de datos entrantes y salientes.

---

### Paso 4: Configurar las Variables de Entorno (`.env`)
El proyecto necesita saber qué claves de API usar y a qué base de datos conectarse.

1. Revisa que exista el archivo `.env` en la raíz de `backend`. Si no existe, copia el archivo de ejemplo:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Abre `.env` y valida los parámetros principales:
   * `DATABASE_URL`: Cadena de conexión a PostgreSQL (por defecto: `postgresql+pg8000://postgres:felipe@localhost:5432/transcriptor_db`).
   * `DEEPSEEK_API_KEY`: Token de acceso para los modelos de extracción de acuerdos.
   * `HUGGINGFACE_API_KEY`: Token para modelos de transcripción.
   * `UPLOAD_DIR`: Carpeta temporal donde se guardan los audios subidos (`storage/audios_temp`).

---

### Paso 5: Preparar la Base de Datos
Tienes dos opciones para la base de datos:

* **Opción A (Recomendada con PostgreSQL):**  
  Asegúrate de que el servicio de PostgreSQL esté iniciado. Puedes correr el script utilitario para crear la base de datos si aún no existe:
  ```powershell
  py scripts/init_db.py
  ```
  Luego, carga la estructura de tablas usando el script SQL ubicado en `../db/db.sql` (ver la [Guía de Carga de Base de Datos](../db/README.md)).

* **Opción B (Automática con SQLite - Modo Rápido):**  
  Si no tienes PostgreSQL configurado todavía, **no te detengas**. El sistema detectará que Postgres no responde y creará automáticamente un archivo SQLite local (`transcriptor.db`) con las tablas y datos de prueba.

---

### Paso 6: Encender el Servidor de la API
Inicia el servidor Uvicorn ejecutando:

```powershell
py -m uvicorn app.main:app --reload --port 8000
```

**Explicación del comando:**
* `app.main:app`: Indica que en el archivo `app/main.py` busque la instancia `app = FastAPI()`.
* `--reload`: Reinicia automáticamente el servidor cada vez que guardes cambios en el código.
* `--port 8000`: Expone el servidor en el puerto 8000.

Cuando el servidor arranque con éxito, verás un mensaje como:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

---

## 🌐 Paso 7: Comprobar que la API está funcionando

Abre tu navegador web e ingresa a las siguientes URLs:

1. **Documentación Interactiva (Swagger UI):**
   👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
   Aquí podrás ver todos los endpoints del sistema (subir audio, consultar acuerdos, listar responsables) y probarlos interactivamente haciendo clic en el botón **"Try it out"**.

2. **Endpoint de Salud del Sistema:**
   👉 [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)  
   Deberá responder un JSON confirmando el estado:
   ```json
   {
     "code": 200,
     "message": "Servicio operativo",
     "data": {
       "status": "online",
       "service": "Transcriptor Maestro API",
       "version": "1.0.0",
       "environment": "development"
     }
   }
   ```

3. **Documentación Alternativa (ReDoc):**
   👉 [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## ❓ Preguntas Frecuentes y Solución de Errores

| Síntoma / Error | Causa | Solución |
| :--- | :--- | :--- |
| `pip: El término 'pip' no se reconoce...` | Python `Scripts` no está en el `PATH` de Windows. | Ejecuta siempre usando el lanzador `py -m pip ...` o activa el entorno virtual (`.\venv\Scripts\Activate.ps1`). |
| `La ejecución de scripts está deshabilitada en este sistema` | Política de seguridad de PowerShell al activar `venv`. | Ejecuta: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| `No fue posible conectar al motor principal... Usando SQLite local` | El servicio de PostgreSQL está apagado o las credenciales en `.env` no coinciden. | La API seguirá funcionando en SQLite de prueba. Para usar Postgres, revisa que esté activo en el puerto 5432. |
| `Address already in use (puerto 8000 ocupado)` | Hay otro proceso usando el puerto 8000. | Cambia el puerto en el comando: `py -m uvicorn app.main:app --reload --port 8001`. |

---

## 🛑 Detener el Servidor
Para apagar el backend en cualquier momento, ve a la terminal donde está corriendo y presiona:
`CTRL + C`
