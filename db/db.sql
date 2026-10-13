-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla Proyectos
CREATE TABLE IF NOT EXISTS proyectos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla Responsables
CREATE TABLE IF NOT EXISTS responsables (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proyecto_id UUID REFERENCES proyectos(id) ON DELETE SET NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    alias_conocidos JSONB DEFAULT '[]'::jsonb,
    email VARCHAR(150) UNIQUE,
    rol VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla Reuniones
CREATE TABLE IF NOT EXISTS reuniones (
    id VARCHAR(36) PRIMARY KEY,
    proyecto_id UUID REFERENCES proyectos(id) ON DELETE SET NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    ruta_audio VARCHAR(500) NOT NULL,
    tamano_mb NUMERIC(8, 2),
    duracion_seg NUMERIC(10, 2),
    estado_proceso VARCHAR(20) DEFAULT 'EN_COLA' CHECK (estado_proceso IN ('EN_COLA', 'PROCESANDO', 'COMPLETADO', 'FALLIDO')),
    estrategia_ia INTEGER DEFAULT 5,
    transcripcion_texto TEXT,
    resumen_ejecutivo TEXT,
    tiempo_procesamiento_seg NUMERIC(8, 2),
    metadatos_audio JSONB DEFAULT '{}'::jsonb,
    error_detalle TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabla Acuerdos
CREATE TABLE IF NOT EXISTS acuerdos (
    id VARCHAR(36) PRIMARY KEY,
    reunion_id VARCHAR(36) NOT NULL REFERENCES reuniones(id) ON DELETE CASCADE,
    responsable_id UUID REFERENCES responsables(id) ON DELETE SET NULL,
    responsable_crudo VARCHAR(150),
    similitud_fuzzy NUMERIC(4, 3) DEFAULT 1.000,
    tarea_desc TEXT NOT NULL,
    fecha_compromiso_texto VARCHAR(100),
    fecha_limite DATE,
    fragmento_original TEXT NOT NULL,
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'completado', 'atrasado')),
    acuerdo_origen_id VARCHAR(36) REFERENCES acuerdos(id) ON DELETE SET NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabla Historial de Estados
CREATE TABLE IF NOT EXISTS historial_estados (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    acuerdo_id VARCHAR(36) NOT NULL REFERENCES acuerdos(id) ON DELETE CASCADE,
    reunion_origen_id VARCHAR(36) REFERENCES reuniones(id) ON DELETE SET NULL,
    estado_anterior VARCHAR(20) NOT NULL,
    estado_nuevo VARCHAR(20) NOT NULL,
    evidencia_texto TEXT,
    fecha_cambio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabla Auditoría IA (El Perceptrón)
CREATE TABLE IF NOT EXISTS auditoria_ia_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reunion_id VARCHAR(36) REFERENCES reuniones(id) ON DELETE CASCADE,
    etapa VARCHAR(50) NOT NULL,
    proveedor VARCHAR(50) NOT NULL,
    estado_binario INTEGER DEFAULT 0 CHECK (estado_binario IN (0, 1)),
    nivel_error INTEGER DEFAULT 4,
    latencia_ms INTEGER,
    conmutacion_vaca BOOLEAN DEFAULT FALSE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de aceleración para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_acuerdos_reunion ON acuerdos(reunion_id);
CREATE INDEX IF NOT EXISTS idx_acuerdos_responsable ON acuerdos(responsable_id);
CREATE INDEX IF NOT EXISTS idx_acuerdos_estado ON acuerdos(estado);
CREATE INDEX IF NOT EXISTS idx_reuniones_estado ON reuniones(estado_proceso);
