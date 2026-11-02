// Contratos del backend (ver backend/FRONTEND_HANDOFF.md). Toda respuesta es ResponseDto<T>.
export interface ResponseDto<T> {
  code: number;
  message: string;
  data: T;
}

export type EstadoReunion = 'EN_COLA' | 'PROCESANDO' | 'COMPLETADO' | 'FALLIDO';
export type EstadoAcuerdo = 'pendiente' | 'completado' | 'atrasado';
export const ESTADOS_ACUERDO: EstadoAcuerdo[] = ['pendiente', 'completado', 'atrasado'];

export interface ReunionUpload {
  id_reunion: string;
  nombre_archivo: string;
  tamano_mb: number;
  estado: EstadoReunion;
  mensaje: string;
}

export interface ReunionEstado {
  id_reunion: string;
  nombre_archivo: string;
  estado: EstadoReunion;
  progreso_estimado: string | null;
  fecha_registro: string;
  fecha_actualizacion: string;
  error_detalle: string | null;
}

export interface ReunionResumen {
  id_reunion: string;
  nombre_archivo: string;
  estado: EstadoReunion;
  duracion_segundos: number | null;
  resumen_ejecutivo: string | null;
  total_acuerdos: number;
}

export interface Acuerdo {
  id_acuerdo: string;
  id_reunion: string;
  tarea_desc: string;
  responsable: string;
  responsable_crudo: string | null;
  responsable_id: string | null;
  similitud_fuzzy: number | null;
  fecha_compromiso: string | null;
  fragmento_original: string;
  estado: EstadoAcuerdo;
  fecha_creacion: string;
}

export interface ReunionDetalle extends ReunionEstado {
  estrategia_utilizada: number | null;
  tiempo_procesamiento_seg: number | null;
  transcripcion: string | null;
  resumen_ejecutivo: string | null;
  acuerdos: Acuerdo[];
}

export interface Responsable {
  id: string;
  nombre_completo: string;
  alias_conocidos: string[];
  email: string | null;
  rol: string | null;
  activo: boolean;
  proyecto_id: string | null;
  creado_en: string;
}

export interface ResponsableCreate {
  nombre_completo: string;
  alias_conocidos: string[];
  email: string | null;
  rol: string | null;
}

export interface EstadoAuditoria {
  perceptron_activo: boolean;
  vaca_primaria: string;
  vaca_replica: string;
  vaca_emergencia: string;
  simulacion_fallo_activa: boolean;
  sla_latencia_maxima_ms: number;
}

export interface Metricas {
  total_ejecuciones: number;
  tasa_exito_porcentaje: number;
  tasa_conmutacion_vaca_porcentaje: number;
  latencia_promedio_ms: number;
  total_conmutaciones_vaca: number;
  alertas_sla: number;
}

export interface LogIA {
  id: string;
  reunion_id: string;
  etapa: string;
  proveedor: string;
  estado_binario: number;
  nivel_error: number;
  latencia_ms: number | null;
  conmutacion_vaca: boolean;
  creado_en: string;
}

export interface EstadoCache {
  tiene_contenido: boolean;
  total_archivos: number;
  total_tamano_mb: number;
  audios_temp: { total_archivos: number; tamano_mb: number };
  salidas: { total_archivos: number; tamano_mb: number };
}

export interface ConfigIA {
  estrategia: number;
  modelo_whisper: string;
  llm_preferido: string;
  modelo_llm: string;
}
