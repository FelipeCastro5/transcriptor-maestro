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
  modo_consenso?: boolean;
}

// ============================================================================
// CONTRATOS FASE 1 & FASE 2: ALERTAS, MLOPS (WER, DRIFT) Y PROMPT REGISTRY
// ============================================================================

export interface AlertaSistema {
  id: string;
  tipo_alerta: string;
  severidad: string;
  acuerdo_id: string | null;
  responsable_id: string | null;
  mensaje: string;
  leida: boolean;
  despachada_webhook: boolean;
  creado_en: string;
}

export interface SchedulerStatus {
  activo: boolean;
  proxima_ejecucion: string | null;
  intervalo_minutos: number;
  total_alertas_activas: number;
  modo: string;
}

export interface BarridoResultado {
  acuerdos_revisados: number;
  acuerdos_atrasados: number;
  omisiones_detectadas: number;
  alertas_generadas: number;
  mensaje: string;
  timestamp: string;
}

export interface AlineacionToken {
  ref: string | null;
  hyp: string | null;
  op: 'MATCH' | 'SUBSTITUTION' | 'INSERTION' | 'DELETION';
  peso: number;
}

export interface CalibrarWER {
  id: string;
  reunion_id: string | null;
  modelo_evaluado: string;
  total_palabras_gt: number;
  total_palabras_hyp: number;
  sustituciones: number;
  eliminaciones: number;
  inserciones: number;
  aciertos: number;
  wer: number;
  wer_porcentaje: number;
  wer_ponderado: number;
  wer_ponderado_porcentaje: number;
  precision_palabra: number;
  precision_palabra_porcentaje: number;
  longitud_relativa: number;
  estado_calidad: string;
  cumple_meta_sprint: boolean;
  alineacion: AlineacionToken[];
  creado_en: string;
}

export interface DataDrift {
  total_palabras_evaluadas: number;
  palabras_unicas_evaluadas: number;
  tamano_vocabulario_base: number;
  palabras_oov_detectadas: string[];
  total_palabras_oov: number;
  ratio_oov: number;
  ratio_oov_porcentaje: number;
  estado_drift: string;
  alerta_drift: boolean;
  recomendacion: string;
}

export interface PromptVersion {
  id: string;
  version: string;
  nombre: string;
  descripcion: string;
  hash_md5: string;
  modelos_compatibles: string[];
  es_activo: boolean;
  prompt_sistema: string;
  creado_en: string;
}

