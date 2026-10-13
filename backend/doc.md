Para entender el flujo completo de tu aplicación y cómo se conectan los endpoints con la lógica pesada de la Inteligencia Artificial y la base de datos, los archivos principales se dividen en diferentes "capas".

Aquí tienes el mapa de los archivos clave y cómo interactúan entre sí en un flujo típico (como subir un audio):

### 1. La Puerta de Entrada (Configuración y Rutas)
* **`backend/app/main.py`**: Es el punto de arranque de FastAPI. Aquí se levanta el servidor, se configuran los CORS (para que el frontend se pueda conectar) y se manejan los errores globales para que todas las respuestas respeten el formato `ResponseDto`.
* **`backend/app/api/v1/router.py`**: Es el "director de tráfico". Agrupa todas las rutas de los distintos archivos y las pone bajo el prefijo `/api/v1/`.

### 2. Los Endpoints (Controladores)
Estos archivos reciben las peticiones HTTP del frontend:
* **`backend/app/api/v1/endpoints/reuniones.py`**: El más importante. Tiene el endpoint `POST /upload` (que recibe el archivo de audio y lanza el proceso en segundo plano) y el endpoint `GET /{id}/estado` (para el *polling* de estado).
* **`backend/app/api/v1/endpoints/acuerdos.py`**: Tiene los endpoints para listar todas las tareas/acuerdos del Kanban y poder actualizar su estado (ej: pasar de 'pendiente' a 'completado').
* **`backend/app/api/v1/endpoints/responsables.py`**: Maneja la creación y listado de los miembros del equipo y sus apodos para el *Fuzzy Matching*.

### 3. La Lógica de Negocio (Servicios)
Aquí es donde ocurre la "magia" antes de tocar la base de datos o la IA:
* **`backend/app/services/reunion_service.py`**: Orquesta todo el flujo. Toma el archivo recibido por el endpoint, crea el registro en la base de datos (con estado "EN_COLA"), guarda el archivo en `storage/audios_temp/` y lanza el procesamiento asíncrono en segundo plano para no congelar la respuesta.
* **`backend/app/services/matching.py`**: Contiene la lógica para corregir los nombres de las personas (Levenshtein/Fuzzy Matching). Convierte un "Juna" devuelto por la IA en el "Juan" que existe en la base de datos.

### 4. El Corazón de IA (Machine Learning y Resiliencia)
Estos archivos son llamados por `reunion_service.py` en segundo plano:
* **`backend/app/services/ai_handler.py`**: Es el motor principal. Toma el audio, lo pasa por Whisper (o similar) para la transcripción en crudo, luego prepara el "prompt" avanzado y se lo envía al modelo (DeepSeek u OpenAI) para que extraiga el resumen y los acuerdos.
* **`backend/app/services/vacas.py`**: (*Hot Failover*) Es tu escudo anti-caídas. Si la IA de DeepSeek o el servidor fallan, "VACAS" detecta el fallo y en menos de 1.5 segundos redirige la petición a otro modelo o a la estrategia offline de emergencia.
* **`backend/app/core/perceptron.py`**: Evalúa la salud del sistema y clasifica qué tipo de error ocurrió (SLA, timeout, etc.).

### 5. Base de Datos (Modelos y Schemas)
* **`backend/app/db/models/`**: Aquí están tus tablas de la base de datos en Postgres (como `reunion.py`, `acuerdo.py`, `responsable.py`), escritas con SQLAlchemy.
* **`backend/app/schemas/`**: Aquí están los esquemas de Pydantic (como `response.py` que estandariza todas tus respuestas con el `ResponseDto`, asegurando que Frontend siempre reciba `{ code, message, data }`).

---

### 🔄 Resumen del Flujo de una Petición (`POST /upload`):
1. El archivo llega al endpoint en **`endpoints/reuniones.py`**.
2. El endpoint se lo pasa a **`reunion_service.py`**.
3. El servicio guarda un registro en la BD usando los modelos de **`db/models/`** y responde al instante con un `202 Accepted` (el formato de respuesta lo da **`schemas/response.py`**).
4. Mientras tanto, en segundo plano, el servicio invoca a **`ai_handler.py`** protegido por **`vacas.py`**.
5. Cuando la IA termina, se usa **`matching.py`** para enlazar las tareas con las personas correctas.
6. Finalmente, se guardan los resultados finales en PostgreSQL.