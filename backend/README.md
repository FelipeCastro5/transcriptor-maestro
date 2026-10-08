# 🎙️ Transcriptor Maestro - Backend REST API

Backend modular empresarial construido con **FastAPI** y **PostgreSQL** para el *Sistema Inteligente de Seguimiento de Acuerdos y Control de Proyectos*, con arquitectura resiliente basada en **El Perceptrón (Megatron)**, contingencia **VACAS** y respuestas 100% estandarizadas bajo el patrón **`ResponseDto<T>`**.

---

## 🚀 Inicio Rápido

### 1. Dependencias
Instala los paquetes de `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Base de Datos (PostgreSQL Local)
* Base de datos: `transcriptor_db`
* Usuario: `postgres`
* Contraseña: `felipe`
* Puerto: `5432`

Las tablas y el sembrado inicial se crean automáticamente al arrancar la aplicación.

### 3. Levantar el Servidor
```bash
python -m uvicorn app.main:app --reload --port 8000
```

* **Documentación interactiva Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Documentación alternativa ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Endpoint de Salud:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📦 Estructura Unificada de Respuesta (`ResponseDto<T>`)

Todos los endpoints (éxito y errores) devuelven estrictamente la estructura:
```json
{
  "code": 200,
  "message": "Operación exitosa",
  "data": { ... } // o null en errores
}
```

### Ejemplos:
* **Éxito (200 / 201 / 202):**
```json
{
  "code": 202,
  "message": "Audio recibido y encolado para procesamiento asíncrono",
  "data": {
    "id_reunion": "MEET-D786EE9B",
    "nombre_archivo": "audio.mp3",
    "estado": "EN_COLA"
  }
}
```
* **Error (400 / 404 / 422 / 500):**
```json
{
  "code": 404,
  "message": "Reunión 'MEET-INVENTADA' no encontrada",
  "data": null
}
```

---

## 🧭 Endpoints Disponibles (Fases 1, 2, 3 y 4)

### 📌 Reuniones (`/api/v1/reuniones`)
* `POST /upload`: Sube audio (`.mp3`, `.wav`), valida y encola el procesamiento asíncrono (`ResponseDto[ReunionUploadResponse]`).
* `POST /{id_reunion}/procesar`: Dispara el pipeline seleccionando una de las 5 estrategias del Handler Dinámico (`ResponseDto[ReunionEstadoResponse]`).
* `GET /{id_reunion}/estado`: Sondeo (polling) del estado de procesamiento (`EN_COLA`, `PROCESANDO`, `COMPLETADO`, `FALLIDO`).
* `GET /{id_reunion}/resultados`: Retorna la transcripción íntegra, el resumen ejecutivo y los acuerdos detectados (`ResponseDto[ReunionDetalleResponse]`).
* `GET /`: Listado general de reuniones registradas en PostgreSQL (`ResponseDto[List[ReunionResumen]]`).

### 📋 Acuerdos y Compromisos (`/api/v1/acuerdos`)
* `GET /`: Listado global de tareas extraídas (`ResponseDto[List[AcuerdoResponse]]`).
* `GET /reunion/{id_reunion}`: Consulta de acuerdos específicos de una reunión (`ResponseDto[List[AcuerdoResponse]]`).
* `PATCH /{id_acuerdo}/estado`: Actualización de estado del compromiso (`pendiente`, `completado`, `atrasado`) con registro en `historial_estados` (`ResponseDto[AcuerdoResponse]`).

### 👥 Catálogo de Responsables (`/api/v1/responsables`)
* `GET /`: Consulta los miembros del equipo y sus alias reconocibles (`ResponseDto[List[ResponsableResponse]]`).
* `POST /`: Registra nuevos miembros y apodos para auto-emparejamiento (`ResponseDto[ResponsableResponse]`).

### 🛡️ Auditoría y Resiliencia (`/api/v1/auditoria`)
* `GET /estado`: Semáforo de salud de proveedores de LLM y estado del Perceptrón.
* `GET /metricas`: Tasa de éxito %, tiempo promedio de respuesta y total de conmutaciones VACA.
* `GET /logs`: Historial de ejecuciones de IA registrado en la tabla `auditoria_ia_logs`.
* `POST /simular-conmutacion`: Chaos Testing para forzar la caída del LLM primario y auditar el rescate en caliente por la VACA réplica.

---

## 🧪 Pruebas Automatizadas
Para ejecutar la suite completa de pruebas unitarias y de integración (15 pruebas):
```bash
python tests/run_tests.py
```
*(Actualmente: 15/15 pruebas superadas con ResponseDto).*
