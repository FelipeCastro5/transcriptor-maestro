Aquí tienes la **Guía de Handoff y Especificación Técnica para tu compañero de Frontend**. Está diseñada para que se la compartas directamente, explicándole los flujos de usuario (UX), las pantallas que debe maquetar y la documentación exacta de cada endpoint que debe consumir en local.



---



# 📘 Manual de Integración Frontend: Transcriptor Maestro



* **Base URL Local:** `http://localhost:8000`

* **Prefijo de API:** `/api/v1`

* **Swagger Interactivo para pruebas:** [http://localhost:8000/docs](http://localhost:8000/docs)

* **CORS:** Ya está habilitado para aceptar peticiones desde cualquier puerto (`localhost:3000`, `5173`, etc.).



---



## 🎨 1. Casos de Uso y Flujos de Experiencia de Usuario (UX)



El frontend se divide en **5 vistas o módulos principales**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   VISTAS FRONTEND                                      │
├─────────────────────┬──────────────────┬─────────────────┬──────────────┬──────────────┤
│ 1. Subida & Config  │ 2. Minuta /      │ 3. Historial de │ 4. Kanban /  │ 5. Equipo /  │
│    (Drag & Drop +   │    Resultados    │    Reuniones    │    Acuerdos  │    Catálogo  │
│    Parámetros IA)   │    (Transcripción│    (Análisis    │    (Estados) │    (Fuzzy M.)│
│                     │    y Acuerdos)   │    Previos)     │              │              │
└─────────────────────┴──────────────────┴─────────────────┴──────────────┴──────────────┘
```



---



### Caso de Uso 1: Carga de Audio, Personalización y Espera Asíncrona (Upload & Polling)

* **Objetivo:** El usuario sube el audio de una reunión, personaliza los parámetros de IA si lo desea, y ve el avance sin que la página se congele.

* **Flujo UX:**
  1. El usuario arrastra un archivo (`.mp3`, `.wav`, etc.) a una zona de carga (*Drag & Drop*).
  2. **Panel de Configuración de IA (Opcional / Desplegable):**
     * **Estrategia IA (`estrategia`):**
       * `5`: Híbrido Maduro con Hot-Failover VACAS (*Recomendado por defecto*).
       * `4`: Prompt Avanzado (optimizado para lenguaje informal/coloquial).
       * `1`: Reglas Lingüísticas Offline (100% local, sin consumo de API).
     * **Tamaño de Modelo Whisper (`modelo_whisper`):** `"small"` (rápido), `"medium"` (*por defecto*), `"large"` (máxima precisión).
     * **Proveedor LLM (`llm_preferido`):** `"deepseek"` (*por defecto*) o `"openai"`.
     * **Modelo LLM (`modelo_llm`):** `"deepseek-chat"`, `"gpt-4o-mini"`, etc.
  3. Al pulsar *"Procesar Reunión"*, se envía el archivo al backend (`POST /reuniones/upload` con los query params elegidos).
  4. El backend responde de inmediato (`202 Accepted`) con un `id_reunion`.
  5. **Manejo en el Front:** Mostrar una pantalla de carga (*Skeleton / Spinner / Barra de progreso*) con el mensaje que devuelve el backend.
  6. El front inicia un sondeo (*polling*) cada **2 a 3 segundos** a `GET /reuniones/{id}/estado`.
  7. Cuando el campo `estado` cambie a `"COMPLETADO"`, redirigir a la **Vista 2 (Detalle / Minuta)**. Si cambia a `"FALLIDO"`, mostrar alerta de error.

---

### Caso de Uso 2: Minuta Inteligente y Auditoría de Tareas (Vista Detalle)

* **Objetivo:** Mostrar los resultados de la reunión: qué se habló, qué tareas salieron y quién las debe hacer.

* **Flujo UX:**
  1. Al cargar la pantalla, llama a `GET /reuniones/{id_reunion}/resultados`.
  2. **Bloque Superior:** Nombre de archivo, tiempo de cómputo en segundos y badge de estado.
  3. **Bloque 1 (Resumen Ejecutivo):** Una tarjeta destacada con el párrafo de 3 a 5 líneas generado por la IA.
  4. **Bloque 2 (Tabla de Acuerdos):** Lista de tareas extraídas.
     * Cada fila muestra: Tarea, **Responsable asignado** (con un indicador de coincidencia Fuzzy ej: $95\%$), Fecha límite y Estado (`Pendiente`, `Completado`, `Atrasado`).
     * **Elemento Clave UX:** Botón o tooltip con *"Ver Cita Textual"*, que muestra el `fragmento_original` del audio para que el usuario audite que la IA no alucinó la tarea.
  5. **Bloque 3 (Transcripción Completa):** Acordeón colapsable con el texto completo del audio.

---

### Caso de Uso 3: Historial de Reuniones y Acceso a Análisis Previos

* **Objetivo:** Permitir al usuario explorar todas las reuniones analizadas anteriormente y reabrir sus actas y compromisos en cualquier momento.

* **Flujo UX:**
  1. Al entrar a la sección de "Historial", el front consume `GET /api/v1/reuniones/`.
  2. Muestra un listado en tabla o tarjetas interactivas con:
     * Nombre del archivo de audio original (`nombre_archivo`)
     * Identificador (`id_reunion`)
     * Badge de estado (`COMPLETADO`, `PROCESANDO`, `FALLIDO`)
     * Extracto del resumen ejecutivo (`resumen_ejecutivo`)
     * Contador de acuerdos (`total_acuerdos`, ej. "3 acuerdos")
  3. **Acción de apertura:** Al hacer clic sobre cualquier fila o botón *"Ver Análisis"*, el frontend navega a la **Vista 2 (Minuta)** cargando los resultados con `GET /api/v1/reuniones/{id_reunion}/resultados`.

---

### Caso de Uso 4: Tablero de Seguimiento de Acuerdos (Kanban o Tabla Interactiva)

* **Objetivo:** Gestionar el ciclo de vida de los compromisos a lo largo de las semanas.

* **Flujo UX:**
  1. Consulta todos los acuerdos con `GET /acuerdos/` (o filtrados por reunión con `?id_reunion=MEET-XXXX`).
  2. Muestra un tablero con 3 columnas o estados:
     * 🟡 **Pendiente**
     * 🟢 **Completado**

     * 🔴 **Atrasado**

  3. El usuario puede cambiar el estado de una tarea (con un menú desplegable, botón o arrastrando la tarjeta).

  4. Al cambiar el estado, el front envía un `PATCH /acuerdos/{id}/estado`.



---



### Caso de Uso 4: Catálogo de Miembros del Equipo (Fuzzy Matching)

* **Objetivo:** Ver y registrar a las personas del equipo con sus apodos para que la IA los reconozca siempre.

* **Flujo UX:**

  1. Lista los miembros con `GET /responsables/`.

  2. Formulario modal para registrar un nuevo integrante (`POST /responsables/`):

     * Nombre Completo: ej. `"Andrés Morales"`

     * Alias / Apodos: ej. `["Andy", "Morales", "Andres"]`

     * Rol: ej. `"Desarrollador Frontend"`



---



## 📡 2. Documentación de Endpoints (Contrato API)



---



### 1. Cargar Audio de Reunión

* **Método:** `POST`

* **Ruta:** `/api/v1/reuniones/upload`

* **Content-Type:** `multipart/form-data`

* **Query Params de Configuración (Opcionales):**
  * `procesar_inmediato` (boolean, default: `true`): Inicia Whisper y LLM de inmediato.
  * `estrategia` (integer, default: `5`): Estrategia de IA:
    * `5` = Híbrido Maduro con failover VACAS (*Recomendado*).
    * `4` = Prompt Avanzado (conversaciones informales).
    * `3` = Whisper + Prompt elemental.
    * `2` = Chunking 30s Hugging Face.
    * `1` = Reglas offline locales (sin LLM).
  * `modelo_whisper` (string, default: `"medium"`): `"small"`, `"medium"`, `"large"`.
  * `llm_preferido` (string, default: `"deepseek"`): `"deepseek"`, `"openai"`.
  * `modelo_llm` (string, default: `"deepseek-chat"`): `"deepseek-chat"`, `"gpt-4o-mini"`, etc.

* **Body (Form-Data):**
  * `file`: Archivo binario de audio (`.mp3`, `.wav`, `.m4a`, `.flac`).

* **Respuesta (`202 Accepted`):**

```json

{

  "id_reunion": "MEET-B01BDEB6",

  "nombre_archivo": "reunion_semanal.mp3",

  "tamano_mb": 14.25,

  "estado": "EN_COLA",

  "mensaje": "Audio recibido. Procesamiento en segundo plano iniciado."

}

```



---



### 2. Sondeo de Estado (Polling)

* **Método:** `GET`

* **Ruta:** `/api/v1/reuniones/{id_reunion}/estado`

* **Respuesta (`200 OK`):**

```json

{

  "id_reunion": "MEET-B01BDEB6",

  "nombre_archivo": "reunion_semanal.mp3",

  "estado": "PROCESANDO", // Valores posibles: "EN_COLA", "PROCESANDO", "COMPLETADO", "FALLIDO"

  "progreso_estimado": "Transcribiendo y analizando con Estrategia 5...",

  "fecha_registro": "2026-10-06T23:30:17Z",

  "fecha_actualizacion": "2026-10-06T23:30:19Z",

  "error_detalle": null

}

```

> **Nota para el Front:** Si `estado === "COMPLETADO"`, detener el polling y consultar el endpoint de resultados.



---



### 3. Obtener Resultados Completos de la Reunión

* **Método:** `GET`

* **Ruta:** `/api/v1/reuniones/{id_reunion}/resultados`

* **Respuesta (`200 OK`):**

```json

{

  "id_reunion": "MEET-B01BDEB6",

  "nombre_archivo": "reunion_semanal.mp3",

  "estado": "COMPLETADO",

  "progreso_estimado": "Procesamiento finalizado con éxito.",

  "estrategia_utilizada": 5,

  "tiempo_procesamiento_seg": 4.12,

  "transcripcion": "Buenas tardes a todos. Juan Pérez debe entregar el reporte...",

  "resumen_ejecutivo": "Se llevó a cabo la sincronización del sprint, priorizando la entrega de métricas y mockups.",

  "acuerdos": [

    {

      "id_acuerdo": "AC-9A1F2C",

      "id_reunion": "MEET-B01BDEB6",

      "tarea_desc": "entregar el informe de métricas de rendimiento",

      "responsable": "Juan Pérez",

      "responsable_crudo": "Juna Pérez",

      "similitud_fuzzy": 0.89,

      "fecha_compromiso": "este viernes 20 de octubre",

      "fragmento_original": "Juan Pérez debe entregar el informe de métricas este viernes...",

      "estado": "pendiente",

      "fecha_creacion": "2026-10-06T23:30:21Z"

    }

  ],

  "fecha_registro": "2026-10-06T23:30:17Z",

  "fecha_actualizacion": "2026-10-06T23:30:21Z"

}

```



---



### 4. Listar Todas las Reuniones (Historial)

* **Método:** `GET`

* **Ruta:** `/api/v1/reuniones/`

* **Respuesta (`200 OK`):**

```json

[

  {

    "id_reunion": "MEET-B01BDEB6",

    "nombre_archivo": "reunion_semanal.mp3",

    "estado": "COMPLETADO",

    "resumen_ejecutivo": "Se sincronizaron pendientes clave...",

    "total_acuerdos": 3

  }

]

```



---



### 5. Listar Acuerdos Globales (Para Kanban / Tablero)

* **Método:** `GET`

* **Ruta:** `/api/v1/acuerdos/`

* **Query Params (Opcional):**

  * `id_reunion` (string): Si solo se quieren las tareas de una reunión específica.

* **Respuesta (`200 OK`):**

```json

[

  {

    "id_acuerdo": "AC-9A1F2C",

    "id_reunion": "MEET-B01BDEB6",

    "tarea_desc": "diseñar los mockups de la interfaz",

    "responsable": "María Gómez",

    "responsable_crudo": "Mary Gómez",

    "similitud_fuzzy": 0.95,

    "fecha_compromiso": "el próximo lunes",

    "fragmento_original": "María Gómez yo me encargo de diseñar los mockups...",

    "estado": "pendiente",

    "fecha_creacion": "2026-10-06T23:30:21Z"

  }

]

```



---



### 6. Actualizar Estado de una Tarea (Completar / Reabrir)

* **Método:** `PATCH`

* **Ruta:** `/api/v1/acuerdos/{id_acuerdo}/estado`

* **Content-Type:** `application/json`

* **Body:**

```json

{

  "estado": "completado", // Valores válidos: "pendiente", "completado", "atrasado"

  "nota_actualizacion": "Entregado en la reunión de cierre" // Opcional

}

```

* **Respuesta (`200 OK`):** Devuelve el objeto del acuerdo actualizado con su nuevo estado.



---



### 7. Consultar y Crear Responsables (Fuzzy Matching)

* **Listar miembros:** `GET /api/v1/responsables/`

  * **Respuesta (`200 OK`):**

    ```json

    [

      {

        "id": "uuid-1234",

        "nombre_completo": "Juan Pérez",

        "alias_conocidos": ["Juan", "Juancho", "Juna", "Pérez"],

        "email": "juan.perez@empresa.com",

        "rol": "Project Manager",

        "activo": true

      }

    ]

    ```

* **Crear nuevo miembro:** `POST /api/v1/responsables/`

  * **Body:**

    ```json

    {

      "nombre_completo": "Andrés Morales",

      "alias_conocidos": ["Andy", "Morales", "Andres"],

      "email": "andres@empresa.com",

      "rol": "DevOps Engineer"

    }

    ```



---



### 8. Panel de Monitoreo / Auditoría (Opcional - Vista Admin)

* `GET /api/v1/auditoria/metricas`:

  * Devuelve: `tasa_exito_porcentaje`, `latencia_promedio_ms`, `total_conmutaciones_vaca`.

* `POST /api/v1/auditoria/simular-conmutacion`:

  * Body: `{"activar_fallo": true}` (Útil para hacer una demo en vivo de cómo el sistema no se cae ante fallos de la IA).



### 9. Diagnóstico y Limpieza de Almacenamiento (Caché en Disco)

* `GET /api/v1/sistema/estado-cache`:
  * Devuelve si hay archivos temporales huérfanos acumulados, conteo de audios y salidas, y el total en MB (`total_tamano_mb`).
  * Ideal para un badge en el Header o panel de Ajustes: *"Caché en disco: 1.2 MB"*.
* `POST /api/v1/sistema/limpiar-cache`:
  * Purga manual a demanda con un botón *"Vaciar Almacenamiento Temporal"*.
  * Query params opcionales: `?solo_audios=true` o `?solo_salidas=true`.

---



## 💡 Consejos de Implementación para el Frontend



1. **Evitar Timeouts:** Al subir el audio, el backend responde en menos de 200 milisegundos con el `HTTP 202` porque el procesamiento corre en segundo plano. Nunca dejes la petición `POST /upload` esperando a que Whisper termine.

2. **Intervalo de Polling:** Configura un `setInterval` de **2.5 segundos** llamando a `GET /reuniones/{id}/estado`. No hagas consultas cada 100 ms para no saturar la red local.

3. **Manejo de Errores HTTP:**

   * `400 Bad Request`: Formato de audio no válido (ej. subieron un `.pdf` o `.exe`).

   * `404 Not Found`: ID de reunión inexistente.

   * `413 Request Entity Too Large`: El audio supera los $250\,\text{MB}$.
