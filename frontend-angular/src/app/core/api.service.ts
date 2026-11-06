import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  Acuerdo, ConfigIA, EstadoAcuerdo, EstadoAuditoria, EstadoCache, LogIA, Metricas,
  ReunionDetalle, ReunionEstado, ReunionResumen, ReunionUpload, Responsable,
  ResponsableCreate, ResponseDto, AlertaSistema, SchedulerStatus, BarridoResultado,
  CalibrarWER, DataDrift, PromptVersion
} from './models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;
  private api = `${this.base}/api/v1`;

  // Convierte errores HTTP en Error con el "message" del ResponseDto del backend.
  private handle<T>(obs: Observable<ResponseDto<T>>): Observable<ResponseDto<T>> {
    return obs.pipe(
      catchError((err: HttpErrorResponse) => {
        const msg = err.status === 0
          ? 'No se pudo conectar con el backend. ¿Está encendido en el puerto 8000?'
          : err.error?.message || `Error HTTP ${err.status}`;
        return throwError(() => new Error(msg));
      })
    );
  }

  private get<T>(url: string, params?: HttpParams) {
    return this.handle(this.http.get<ResponseDto<T>>(url, { params }));
  }

  private send<T>(method: 'post' | 'patch', url: string, body: unknown, params?: HttpParams) {
    return this.handle(this.http.request<ResponseDto<T>>(method, url, { body, params }));
  }

  health() {
    return this.get<Record<string, unknown>>(`${this.base}/health`);
  }

  // Reuniones
  subirAudio(file: File, config: ConfigIA) {
    const form = new FormData();
    form.append('file', file);
    const params = new HttpParams({ fromObject: { ...config, procesar_inmediato: true } });
    return this.send<ReunionUpload>('post', `${this.api}/reuniones/upload`, form, params);
  }

  estadoReunion(id: string) {
    return this.get<ReunionEstado>(`${this.api}/reuniones/${id}/estado`);
  }

  resultadosReunion(id: string) {
    return this.get<ReunionDetalle>(`${this.api}/reuniones/${id}/resultados`);
  }

  listarReuniones() {
    return this.get<ReunionResumen[]>(`${this.api}/reuniones/`);
  }

  // Acuerdos
  listarAcuerdos(idReunion?: string) {
    const params = idReunion ? new HttpParams().set('id_reunion', idReunion) : undefined;
    return this.get<Acuerdo[]>(`${this.api}/acuerdos/`, params);
  }

  cambiarEstadoAcuerdo(id: string, estado: EstadoAcuerdo, nota?: string) {
    return this.send<Acuerdo>('patch', `${this.api}/acuerdos/${id}/estado`, {
      estado,
      nota_actualizacion: nota ?? null,
    });
  }

  // Responsables
  listarResponsables() {
    return this.get<Responsable[]>(`${this.api}/responsables/`);
  }

  crearResponsable(data: ResponsableCreate) {
    return this.send<Responsable>('post', `${this.api}/responsables/`, data);
  }

  // Auditoría y sistema
  estadoAuditoria() {
    return this.get<EstadoAuditoria>(`${this.api}/auditoria/estado`);
  }

  metricas() {
    return this.get<Metricas>(`${this.api}/auditoria/metricas`);
  }

  logs() {
    return this.get<LogIA[]>(`${this.api}/auditoria/logs`, new HttpParams().set('limite', 50));
  }

  simularFallo(activar: boolean) {
    return this.send<Record<string, unknown>>('post', `${this.api}/auditoria/simular-conmutacion`, { activar_fallo: activar });
  }

  estadoCache() {
    return this.get<EstadoCache>(`${this.api}/sistema/estado-cache`);
  }

  limpiarCache() {
    return this.send<Record<string, unknown>>('post', `${this.api}/sistema/limpiar-cache`, null);
  }

  // Alertas y Scheduler (Fase 1: Curva de Espacios Iguales)
  listarAlertas(soloNoLeidas: boolean = false) {
    const params = new HttpParams().set('solo_no_leidas', soloNoLeidas);
    return this.get<AlertaSistema[]>(`${this.api}/sistema/alertas`, params);
  }

  marcarAlertaLeida(idAlerta: string) {
    return this.send<AlertaSistema>('post', `${this.api}/sistema/alertas/${idAlerta}/marcar-leida`, {});
  }

  estadoScheduler() {
    return this.get<SchedulerStatus>(`${this.api}/sistema/scheduler/estado`);
  }

  ejecutarBarridoScheduler() {
    return this.send<BarridoResultado>('post', `${this.api}/sistema/scheduler/ejecutar`, {});
  }

  // MLOps: Calibración WER, Data Drift y Prompt Registry (Fase 2)
  calibrarWER(body: { texto_referencia: string; texto_hipotesis?: string; reunion_id?: string; modelo_evaluado?: string }) {
    return this.send<CalibrarWER>('post', `${this.api}/auditoria/calibrar-wer`, body);
  }

  listarCalibraciones() {
    return this.get<CalibrarWER[]>(`${this.api}/auditoria/calibraciones`);
  }

  analizarDataDrift(body: { texto?: string; reunion_id?: string; vocabulario_adicional?: string[] }) {
    return this.send<DataDrift>('post', `${this.api}/auditoria/data-drift`, body);
  }

  listarPrompts() {
    return this.get<PromptVersion[]>(`${this.api}/auditoria/prompts-historial`);
  }

  activarPrompt(versionId: string) {
    return this.send<PromptVersion>('post', `${this.api}/auditoria/prompts-activar`, { version_id: versionId });
  }
}
