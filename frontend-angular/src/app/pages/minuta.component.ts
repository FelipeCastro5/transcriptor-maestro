import { Component, OnInit, inject, input, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { ReunionDetalle } from '../core/models';
import { TablaAcuerdosComponent } from '../shared/tabla-acuerdos.component';

@Component({
  selector: 'app-minuta',
  imports: [RouterLink, TablaAcuerdosComponent, DatePipe],
  template: `
    @if (error()) {
      <section class="card"><p class="error">{{ error() }}</p><a routerLink="/historial">← Historial</a></section>
    } @else if (!det()) {
      <div class="spinner"></div>
    } @else {
      @let d = det()!;
      @let meta = d.metadatos_audio;
      @let tiempos = meta?.tiempos;
      @let config = meta?.configuracion;
      @let archivo = meta?.archivo;
      @let resultados = meta?.resultados;

      <section class="card">
        <a class="link" routerLink="/historial">← Historial</a>
        <div class="row-between">
          <div>
            <h2>{{ d.nombre_archivo }}</h2>
            <p class="muted">
              {{ d.id_reunion }} · Estrategia {{ d.estrategia_utilizada ?? '—' }} · {{ d.tiempo_procesamiento_seg ?? '—' }} s de cómputo
            </p>
          </div>
          <div style="display: flex; align-items: center; gap: 10px;">
            @if (d.estado === 'EN_COLA' || d.estado === 'PROCESANDO') {
              <button class="danger mini" [disabled]="cancelando()" (click)="detener()">
                {{ cancelando() ? 'Cancelando…' : '⏹ Detener procesamiento' }}
              </button>
            }
            <span [class]="'badge ' + d.estado">{{ d.estado }}</span>
          </div>
        </div>
        @if (d.error_detalle && d.estado !== 'CANCELADO') { <p class="error">{{ d.error_detalle }}</p> }
        @if (d.estado === 'CANCELADO') { <p class="muted">{{ d.progreso_estimado || 'Procesamiento cancelado por el usuario.' }}</p> }
      </section>

      <!-- Pestañas internas de la reunión -->
      <div class="tabs-minuta">
        <button [class.activo]="tabActiva() === 'minuta'" (click)="tabActiva.set('minuta')">
          📝 Minuta y Acuerdos
        </button>
        <button [class.activo]="tabActiva() === 'metadata'" (click)="tabActiva.set('metadata')">
          ⚙️ Metadata y Configuración
        </button>
      </div>

      @if (tabActiva() === 'minuta') {
        <section class="card highlight">
          <h3>Resumen ejecutivo</h3>
          <p>{{ d.resumen_ejecutivo || 'Sin resumen disponible.' }}</p>
        </section>

        <section class="card">
          <h3>Acuerdos detectados ({{ d.acuerdos.length }})</h3>
          <app-tabla-acuerdos [acuerdos]="d.acuerdos" (cambio)="cargar()" />
        </section>

        <section class="card">
          <details>
            <summary>Transcripción completa</summary>
            <p class="transcripcion">{{ d.transcripcion || 'Sin transcripción.' }}</p>
          </details>
        </section>
      } @else {
        <!-- PESTAÑA DE METADATA Y CONFIGURACIÓN -->
        <section class="stats">
          <div class="stat">
            <span>Carga del audio</span>
            <strong class="stat-fecha">{{ fechaUtc(tiempos?.fecha_carga_utc || d.fecha_registro) | date:'dd/MM/yyyy HH:mm:ss' }}</strong>
            <span class="small muted">Recepción en servidor</span>
          </div>
          <div class="stat">
            <span>Finalización / Cierre</span>
            <strong class="stat-fecha">
              @if (tiempos?.fecha_fin_proceso_utc) {
                {{ fechaUtc(tiempos?.fecha_fin_proceso_utc) | date:'dd/MM/yyyy HH:mm:ss' }}
              } @else if (d.estado === 'COMPLETADO' || d.estado === 'FALLIDO' || d.estado === 'CANCELADO') {
                {{ fechaUtc(d.fecha_actualizacion) | date:'dd/MM/yyyy HH:mm:ss' }}
              } @else {
                En progreso…
              }
            </strong>
            <span class="small muted">Estado: {{ d.estado }}</span>
          </div>
          <div class="stat">
            <span>Tiempo total</span>
            <strong>{{ (tiempos?.tiempo_total_seg ?? d.tiempo_procesamiento_seg) !== null && (tiempos?.tiempo_total_seg ?? d.tiempo_procesamiento_seg) !== undefined ? (tiempos?.tiempo_total_seg ?? d.tiempo_procesamiento_seg) + ' s' : '—' }}</strong>
            <span class="small muted">
              @if (tiempos?.tiempo_asr_seg !== null && tiempos?.tiempo_asr_seg !== undefined) {
                ASR: {{ tiempos?.tiempo_asr_seg }} s · LLM: {{ tiempos?.tiempo_llm_seg ?? '—' }} s
              } @else {
                Cómputo acumulado
              }
            </span>
          </div>
          <div class="stat">
            <span>Archivo fuente</span>
            <strong>{{ (archivo?.tamano_mb ?? d.tamano_mb) !== null && (archivo?.tamano_mb ?? d.tamano_mb) !== undefined ? (archivo?.tamano_mb ?? d.tamano_mb) + ' MB' : '—' }}</strong>
            <span class="small muted">
              {{ archivo?.tipo_entrada || 'Audio' }}
              @if (archivo?.duracion_audio_seg ?? d.duracion_segundos) {
                · Duración: {{ formatearDuracion(archivo?.duracion_audio_seg ?? d.duracion_segundos) }}
              }
            </span>
          </div>
        </section>

        <section class="grid-2">
          <div class="card">
            <h3>🎛️ Configuración de Procesamiento IA</h3>
            <table class="meta-table">
              <tbody>
                <tr>
                  <th>Estrategia aplicada</th>
                  <td><strong>{{ config?.estrategia_nombre || ('Estrategia ' + (d.estrategia_utilizada ?? '—')) }}</strong></td>
                </tr>
                <tr>
                  <th>Modelo Whisper (ASR)</th>
                  <td><code>{{ config?.modelo_whisper || '—' }}</code></td>
                </tr>
                <tr>
                  <th>Proveedor LLM preferido</th>
                  <td><code>{{ config?.llm_preferido || '—' }}</code></td>
                </tr>
                <tr>
                  <th>Modelo LLM específico</th>
                  <td><code>{{ config?.modelo_llm || '—' }}</code></td>
                </tr>
                <tr>
                  <th>Modo Consenso Dual</th>
                  <td>
                    <span class="chip" [class.chip-ok]="config?.modo_consenso">
                      {{ config?.modo_consenso ? 'Activo (DeepSeek + OpenAI paralelo)' : 'Desactivado (Flujo único)' }}
                    </span>
                  </td>
                </tr>
                <tr>
                  <th>Fragmentación (Chunking 30s)</th>
                  <td>{{ config?.chunking_habilitado ? 'Habilitada (stride 5s)' : 'Desactivada' }}</td>
                </tr>
                <tr>
                  <th>Prompt Registry</th>
                  <td>
                    @if (config?.prompt_utilizado; as prm) {
                      <code>{{ prm.id }}</code> ({{ prm.version }}) · MD5: <code>{{ prm.hash_md5 }}</code>
                    } @else {
                      <span class="muted">No aplica / No registrado</span>
                    }
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="card">
            <h3>📄 Trazabilidad de Archivo y Salida</h3>
            <table class="meta-table">
              <tbody>
                <tr>
                  <th>ID de reunión</th>
                  <td><code>{{ d.id_reunion }}</code></td>
                </tr>
                <tr>
                  <th>Proyecto asociado</th>
                  <td><code>{{ meta?.proyecto_id || 'PROJ-DEFAULT' }}</code></td>
                </tr>
                <tr>
                  <th>Nombre del archivo</th>
                  <td>{{ archivo?.nombre_original || d.nombre_archivo }}</td>
                </tr>
                <tr>
                  <th>Inicio de ejecución IA</th>
                  <td>
                    @if (tiempos?.fecha_inicio_proceso_utc) {
                      {{ fechaUtc(tiempos?.fecha_inicio_proceso_utc) | date:'dd/MM/yyyy HH:mm:ss' }}
                    } @else {
                      <span class="muted">No iniciado / Previo</span>
                    }
                  </td>
                </tr>
                <tr>
                  <th>Volumen transcrito</th>
                  <td>{{ resultados?.transcripcion_palabras ?? 0 }} palabras · {{ resultados?.transcripcion_caracteres ?? 0 }} caracteres</td>
                </tr>
                <tr>
                  <th>Acuerdos extraídos</th>
                  <td><strong>{{ resultados?.total_acuerdos_extraidos ?? d.acuerdos.length }}</strong> acuerdo(s)</td>
                </tr>
                @if (resultados?.cierres_historicos_detectados !== undefined) {
                  <tr>
                    <th>Cierres históricos detectados</th>
                    <td>{{ resultados?.cierres_historicos_detectados }} acuerdo(s) cerrado(s)</td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </section>

        <section class="card">
          <h3>⚡ Traza de Proveedores IA (VACAS &amp; Perceptrón)</h3>
          @if (!d.auditoria_logs || d.auditoria_logs.length === 0) {
            <p class="muted">No se registraron llamadas a proveedores LLM externos para esta reunión (modo offline o cancelación temprana).</p>
          } @else {
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Etapa</th>
                    <th>Proveedor efectivo</th>
                    <th>Latencia</th>
                    <th>Conmutación VACA</th>
                    <th>Estado</th>
                    <th>Hora UTC/Local</th>
                  </tr>
                </thead>
                <tbody>
                  @for (log of d.auditoria_logs; track log.id) {
                    <tr>
                      <td><strong>{{ log.etapa }}</strong></td>
                      <td><code>{{ log.proveedor }}</code></td>
                      <td>{{ log.latencia_ms ?? '—' }} ms</td>
                      <td>{{ log.conmutacion_vaca ? 'Sí (Failover activado)' : 'No (Primario)' }}</td>
                      <td>
                        <span [class]="log.estado_binario === 0 ? 'badge COMPLETADO' : 'badge FALLIDO'">
                          {{ log.estado_binario === 0 ? 'Éxito' : 'Fallo (Nivel ' + log.nivel_error + ')' }}
                        </span>
                      </td>
                      <td class="muted small">{{ fechaUtc(log.creado_en) | date:'dd/MM/yyyy HH:mm:ss' }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </section>
      }
    }
  `,
  styles: [`
    .tabs-minuta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .tabs-minuta button {
      background: #e5e7eb;
      color: #374151;
      border: 1px solid transparent;
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
    }
    .tabs-minuta button:hover {
      background: #d1d5db;
    }
    .tabs-minuta button.activo {
      background: var(--primary);
      color: #fff;
    }
    .stat-fecha {
      font-size: 18px !important;
      line-height: 1.3;
    }
    .meta-table th {
      width: 42%;
      text-transform: none;
      font-size: 13px;
      color: var(--muted);
      font-weight: 600;
    }
    .meta-table td {
      font-size: 13px;
    }
    .chip-ok {
      background: #dcfce7;
      color: #166534;
    }
  `]
})
export class MinutaComponent implements OnInit {
  private api = inject(ApiService);
  id = input.required<string>(); // viene del parámetro de ruta :id
  det = signal<ReunionDetalle | null>(null);
  tabActiva = signal<'minuta' | 'metadata'>('minuta');
  cancelando = signal(false);
  error = signal('');

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.api.resultadosReunion(this.id()).subscribe({
      next: (r) => this.det.set(r.data),
      error: (e: Error) => this.error.set(e.message),
    });
  }

  fechaUtc(valor?: string | null): string | null {
    if (!valor) return null;
    if (valor.endsWith('Z') || /[+-]\d{2}:\d{2}$/.test(valor)) return valor;
    return `${valor}Z`;
  }

  formatearDuracion(segundos?: number | null): string {
    if (segundos === null || segundos === undefined) return '—';
    const total = Math.round(segundos);
    const min = Math.floor(total / 60);
    const seg = total % 60;
    return min > 0 ? `${min}m ${seg}s` : `${seg}s`;
  }

  detener() {
    if (this.cancelando()) return;
    this.cancelando.set(true);
    this.api.cancelarReunion(this.id()).subscribe({
      next: () => {
        this.cancelando.set(false);
        this.cargar();
      },
      error: (e: Error) => {
        this.cancelando.set(false);
        this.error.set(e.message);
      },
    });
  }
}
