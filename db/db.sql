-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTA: Los identificadores son VARCHAR(36) para coincidir con los modelos SQLAlchemy
-- del backend (ej. 'PROJ-DEFAULT', 'MEET-XXXXXXXX', 'AC-XXXXXX' o UUIDs en texto).

-- 1. Tabla Proyectos
CREATE TABLE IF NOT EXISTS proyectos (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 2. Tabla Responsables
CREATE TABLE IF NOT EXISTS responsables (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    proyecto_id VARCHAR(36) REFERENCES proyectos(id) ON DELETE SET NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    alias_conocidos JSON DEFAULT '[]'::json,
    email VARCHAR(150) UNIQUE,
    rol VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 3. Tabla Reuniones
CREATE TABLE IF NOT EXISTS reuniones (
    id VARCHAR(36) PRIMARY KEY,
    proyecto_id VARCHAR(36) REFERENCES proyectos(id) ON DELETE SET NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_audio VARCHAR(500) NOT NULL,
    tamano_mb DOUBLE PRECISION,
    duracion_seg DOUBLE PRECISION,
    estado_proceso VARCHAR(20) NOT NULL DEFAULT 'EN_COLA' CHECK (estado_proceso IN ('EN_COLA', 'PROCESANDO', 'COMPLETADO', 'FALLIDO')),
    estrategia_ia INTEGER DEFAULT 5,
    transcripcion_texto TEXT,
    resumen_ejecutivo TEXT,
    tiempo_procesamiento_seg DOUBLE PRECISION,
    metadatos_audio JSON DEFAULT '{}'::json,
    error_detalle TEXT,
    progreso_estimado VARCHAR(255) DEFAULT 'Audio recibido',
    creado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    actualizado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 4. Tabla Acuerdos
CREATE TABLE IF NOT EXISTS acuerdos (
    id VARCHAR(36) PRIMARY KEY,
    reunion_id VARCHAR(36) NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    responsable_id VARCHAR(36) REFERENCES responsables(id) ON DELETE SET NULL,
    responsable_crudo VARCHAR(150),
    responsable VARCHAR(150) NOT NULL,
    similitud_fuzzy DOUBLE PRECISION DEFAULT 1.0,
    tarea_desc TEXT NOT NULL,
    fecha_compromiso VARCHAR(100),
    fecha_limite DATE,
    fragmento_original TEXT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'completado', 'atrasado')),
    acuerdo_origen_id VARCHAR(36) REFERENCES acuerdos(id) ON DELETE SET NULL,
    creado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    actualizado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 5. Tabla Historial de Estados
CREATE TABLE IF NOT EXISTS historial_estados (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    acuerdo_id VARCHAR(36) NOT NULL REFERENCES acuerdos(id) ON DELETE CASCADE,
    reunion_origen_id VARCHAR(36) REFERENCES reuniones(id) ON DELETE SET NULL,
    estado_anterior VARCHAR(20) NOT NULL,
    estado_nuevo VARCHAR(20) NOT NULL,
    evidencia_texto TEXT,
    fecha_cambio TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 6. Tabla Auditoría IA (El Perceptrón)
CREATE TABLE IF NOT EXISTS auditoria_ia_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    reunion_id VARCHAR(36) NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    etapa VARCHAR(50) NOT NULL,
    proveedor VARCHAR(50) NOT NULL,
    estado_binario INTEGER DEFAULT 0 CHECK (estado_binario IN (0, 1)),
    nivel_error INTEGER DEFAULT 4,
    latencia_ms INTEGER,
    conmutacion_vaca BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- 7. Tabla Alertas del Sistema (Curva de Espacios Iguales y Supervisión)
CREATE TABLE IF NOT EXISTS alertas_sistema (
    id VARCHAR(36) PRIMARY KEY DEFAULT uuid_generate_v4()::text,
    proyecto_id VARCHAR(36) REFERENCES proyectos(id) ON DELETE SET NULL,
    reunion_id VARCHAR(36) REFERENCES reuniones(id) ON DELETE SET NULL,
    acuerdo_id VARCHAR(36) REFERENCES acuerdos(id) ON DELETE SET NULL,
    tipo_alerta VARCHAR(50) NOT NULL,
    nivel_severidad VARCHAR(20) NOT NULL DEFAULT 'WARNING',
    titulo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    webhook_enviado BOOLEAN NOT NULL DEFAULT FALSE,
    creada_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc'),
    actualizada_en TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'utc')
);

-- Índices de aceleración para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_acuerdos_reunion ON acuerdos(reunion_id);
CREATE INDEX IF NOT EXISTS idx_acuerdos_responsable ON acuerdos(responsable_id);
CREATE INDEX IF NOT EXISTS idx_acuerdos_estado ON acuerdos(estado);
CREATE INDEX IF NOT EXISTS idx_reuniones_estado ON reuniones(estado_proceso);
CREATE INDEX IF NOT EXISTS idx_alertas_leida ON alertas_sistema(leida);
CREATE INDEX IF NOT EXISTS idx_alertas_tipo ON alertas_sistema(tipo_alerta);

-- ============================================================================
-- 8. TABLA: EVALUACIONES_CALIBRACION (Telemetría MLOps: WER, WER_w, Data Drift)
-- ============================================================================
CREATE TABLE IF NOT EXISTS evaluaciones_calibracion (
    id VARCHAR(36) PRIMARY KEY,
    reunion_id VARCHAR(36) REFERENCES reuniones(id) ON DELETE SET NULL,
    modelo_evaluado VARCHAR(50) DEFAULT 'whisper-medium',
    total_palabras_gt INTEGER NOT NULL,
    total_palabras_hyp INTEGER NOT NULL,
    sustituciones INTEGER DEFAULT 0,
    eliminaciones INTEGER DEFAULT 0,
    inserciones INTEGER DEFAULT 0,
    aciertos INTEGER DEFAULT 0,
    wer DOUBLE PRECISION NOT NULL,
    wer_ponderado DOUBLE PRECISION NOT NULL,
    precision_palabra DOUBLE PRECISION NOT NULL,
    longitud_relativa DOUBLE PRECISION NOT NULL,
    data_drift_ratio DOUBLE PRECISION DEFAULT 0.0,
    estado_calidad VARCHAR(50) DEFAULT 'OPTIMO',
    detalles_alineacion JSONB,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_eval_reunion ON evaluaciones_calibracion(reunion_id);
CREATE INDEX IF NOT EXISTS idx_eval_creado ON evaluaciones_calibracion(creado_en);

