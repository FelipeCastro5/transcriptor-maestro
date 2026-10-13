# 🗄️ Guía de Base de Datos: Carga de Script SQL (`db.sql`)

Esta guía explica en detalle cómo crear y cargar la base de datos relacional para el sistema **Transcriptor Maestro** utilizando el script [`db.sql`](./db.sql).

---

## 📌 Resumen del Esquema de Base de Datos

El script [`db.sql`](./db.sql) inicializa la estructura necesaria para soportar el flujo de transcripción, extracción de acuerdos con IA y auditoría:

| Elemento | Tipo | Descripción |
| :--- | :--- | :--- |
| **`uuid-ossp`** | Extensión | Habilita la generación de identificadores únicos universales (`uuid_generate_v4()`). |
| **`proyectos`** | Tabla | Almacena los proyectos o iniciativas que agrupan las reuniones. |
| **`responsables`** | Tabla | Guarda los miembros del equipo, roles y su lista de alias (`alias_conocidos` en formato JSONB) para el motor de *Fuzzy Matching*. |
| **`reuniones`** | Tabla | Registra los audios cargados, duración, tamaño, estado del proceso (`EN_COLA`, `PROCESANDO`, `COMPLETADO`, `FALLIDO`), transcripción y resumen. |
| **`acuerdos`** | Tabla | Compromisos y tareas extraídos por la IA, asociados a una reunión y a un responsable asignado. |
| **`historial_estados`** | Tabla | Auditoría de cambios de estado de cada acuerdo (pendiente, completado, atrasado) con evidencia textual. |
| **`auditoria_ia_logs`** | Tabla | Registros de rendimiento y resiliencia de los modelos de IA (latencia, proveedor, conmutación VACAS y El Perceptrón). |
| **Índices** | Optimización | 4 índices para acelerar búsquedas por reunión, responsable y estados de proceso. |

---

## 🔑 Credenciales por Defecto del Proyecto

El backend está configurado en su archivo `.env` con las siguientes credenciales locales estándar:
* **Motor:** PostgreSQL (v14 o superior recomendado)
* **Host:** `localhost` (o `127.0.0.1`)
* **Puerto:** `5432`
* **Usuario:** `postgres`
* **Contraseña:** `felipe`
* **Nombre de la Base de Datos:** `transcriptor_db`

*(Si tus credenciales locales son distintas, solo debes cambiarlas en el archivo `backend/.env`)*.

---

## 🚀 Métodos para Cargar el Script `db.sql`

Elige el método que te resulte más cómodo:

---

### Método 1: Usando pgAdmin 4 (Interfaz Gráfica - Recomendado)

1. Abre **pgAdmin 4** e inicia sesión con tu contraseña de PostgreSQL.
2. En el panel izquierdo (**Browser**), despliega:
   `Servers` ➔ `PostgreSQL (local)` ➔ `Databases`.
3. Haz clic derecho sobre **Databases** y selecciona **Create** ➔ **Database...**.
   * En **Database**, escribe: `transcriptor_db`
   * En **Owner**, selecciona: `postgres`
   * Haz clic en **Save**.
4. Haz clic derecho sobre la base de datos recién creada (`transcriptor_db`) y selecciona **Query Tool** (Herramienta de consultas).
5. Abre el script SQL:
   * Puedes hacer clic en el ícono de carpeta **Open File** (Ctrl + O) y seleccionar el archivo `db.sql` ubicado en:
     `c:\MisProyectos\ECCI\trasncriptor maestro\prototipos\db\db.sql`
   * *O simplemente abre el archivo en tu editor, copia todo el texto y pégalo en la ventana de consultas de pgAdmin.*
6. Presiona la tecla **F5** o haz clic en el botón **Execute/Run** (ícono de triángulo ▶️).
7. En la pestaña inferior **Messages** verás:
   ```text
   CREATE EXTENSION
   CREATE TABLE
   CREATE TABLE
   ...
   CREATE INDEX
   Query returned successfully in ... msec.
   ```

---

### Método 2: Usando la Terminal con `psql` (Consola de Comandos)

Si prefieres la terminal de Windows (PowerShell o CMD):

1. **Crear la base de datos (si aún no existe):**
   ```powershell
   # Ingresar a psql como superusuario
   psql -U postgres -h localhost
   ```
   *(Escribe tu contraseña cuando te la solicite).*

   Dentro de la consola interactiva de PostgreSQL, ejecuta:
   ```sql
   CREATE DATABASE transcriptor_db;
   \q
   ```

2. **Ejecutar el archivo `db.sql` sobre la base de datos creada:**
   Desde la carpeta `prototipos/db` ejecuta:
   ```powershell
   psql -U postgres -h localhost -d transcriptor_db -f db.sql
   ```
   *(Ingresa tu contraseña cuando sea requerida).*

---

### Método 3: Usando DBeaver o VS Code (Database Client)

1. Abre tu cliente de base de datos preferido (DBeaver, DataGrip o la extensión *Database Client* / *PostgreSQL* en VS Code).
2. Conéctate a tu servidor local de PostgreSQL.
3. Crea la base de datos `transcriptor_db`.
4. Abre el archivo `db.sql` en un editor SQL vinculado a `transcriptor_db`.
5. Ejecuta todo el script (**Execute Script** o `Ctrl + Alt + X`).

---

### Método 4: Asistido con Python (Creación de la Base de Datos)
El backend incluye un script en Python que puede verificar y crear la base de datos `transcriptor_db` automáticamente si tienes las credenciales por defecto:

```powershell
cd "c:\MisProyectos\ECCI\trasncriptor maestro\prototipos\backend"
py scripts/init_db.py
```
*Salida esperada:*
```text
[OK] Base de datos 'transcriptor_db' creada exitosamente en PostgreSQL local.
```
*(Luego de crear la base de datos con este comando, ejecuta el script `db.sql` con el Método 1 o 2 para crear las tablas e índices)*.

---

## 🔍 Verificación Post-Carga

Para confirmar que todas las tablas fueron creadas exitosamente, ejecuta la siguiente consulta en tu cliente SQL o `psql`:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

**Resultado esperado (6 tablas):**
1. `acuerdos`
2. `auditoria_ia_logs`
3. `historial_estados`
4. `proyectos`
5. `responsables`
6. `reuniones`

---

## ⚠️ Errores Comunes y Soluciones

* **Error: `permission denied to create extension "uuid-ossp"`**  
  *Causa:* El usuario que ejecuta el script no tiene privilegios de superusuario.  
  *Solución:* Asegúrate de conectarte con el usuario principal `postgres`.

* **Error: `database "transcriptor_db" does not exist`**  
  *Causa:* Intentaste ejecutar `db.sql` antes de crear la base de datos contenedor.  
  *Solución:* Crea primero la base de datos vacía llamada `transcriptor_db` y luego ejecuta el script dentro de ella.

* **Error: `password authentication failed for user "postgres"`**  
  *Causa:* La contraseña ingresada no coincide con la configurada en tu instalación de PostgreSQL.  
  *Solución:* Si tu contraseña no es `felipe`, actualiza la clave en el comando y en la variable `DATABASE_URL` del archivo `backend/.env`.
