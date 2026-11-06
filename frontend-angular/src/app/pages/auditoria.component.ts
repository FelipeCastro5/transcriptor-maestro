import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe, DecimalPipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Observable, forkJoin } from 'rxjs';
import { ApiService } from '../core/api.service';
import {
  EstadoAuditoria, EstadoCache, LogIA, Metricas, ResponseDto,
  CalibrarWER, DataDrift, PromptVersion
} from '../core/models';

@Component({
  selector: 'app-auditoria',
  imports: [DatePipe, DecimalPipe, FormsModule],
  template: `
    @if (msg()) { <p class="success">{{ msg() }}</p> }
    @if (error()) { <p class="error">{{ error() }}</p> }

    <!-- Sub-Navegación de Secciones MLOps -->
    <div class="tabs-mlops">
      <button [class.activo]="seccionActiva() === 'telemetria'" (click)="seccionActiva.set('telemetria')">
        📊 Telemetría VACAS & Perceptrón
      </button>
      <button [class.activo]="seccionActiva() === 'calibracion'" (click)="seccionActiva.set('calibracion')">
        🎯 Calibración de WER & WER Ponderado
      </button>
      <button [class.activo]="seccionActiva() === 'drift'" (click)="seccionActiva.set('drift')">
        🌊 Detección de Data Drift
      </button>
      <button [class.activo]="seccionActiva() === 'prompts'" (click)="seccionActiva.set('prompts')">
        📜 Prompt Registry & Versiones
      </button>
    </div>

    <!-- SECCIÓN 1: TELEMETRÍA Y CONTINGENCIA VACAS -->
    @if (seccionActiva() === 'telemetria') {
      @if (estado() && metricas() && cache()) {
        @let m = metricas()!;
        @let e = estado()!;
        @let c = cache()!;
        <section class="stats">
          <div class="stat"><span>Tasa de éxito</span><strong>{{ m.tasa_exito_porcentaje }}%</strong></div>
          <div class="stat"><span>Latencia promedio</span><strong>{{ m.latencia_promedio_ms }} ms</strong></div>
          <div class="stat"><span>Conmutaciones VACA</span><strong>{{ m.total_conmutaciones_vaca }}</strong></div>
          <div class="stat"><span>Ejecuciones IA</span><strong>{{ m.total_ejecuciones }}</strong></div>
        </section>

        <section class="grid-2">
          <div class="card">
            <h3>Cadena de proveedores (VACAS)</h3>
            <p>Primaria: <strong>{{ e.vaca_primaria }}</strong></p>
            <p>Réplica: <strong>{{ e.vaca_replica }}</strong></p>
            <p>Emergencia: <strong>{{ e.vaca_emergencia }}</strong></p>
            <p class="muted">SLA de latencia: {{ e.sla_latencia_maxima_ms }} ms</p>
            <button [class.danger]="e.simulacion_fallo_activa" (click)="accion(api.simularFallo(!e.simulacion_fallo_activa))">
              {{ e.simulacion_fallo_activa ? 'Desactivar simulación de caída' : 'Simular caída del LLM primario (Chaos)' }}
            </button>
          </div>

          <div class="card">
            <h3>Almacenamiento temporal</h3>
            <p>{{ c.total_archivos }} archivo(s) · {{ c.total_tamano_mb }} MB</p>
            <p class="muted small">Audios: {{ c.audios_temp.total_archivos }} · Salidas: {{ c.salidas.total_archivos }}</p>
            <button [disabled]="!c.tiene_contenido" (click)="accion(api.limpiarCache())">Vaciar almacenamiento temporal</button>
          </div>
        </section>

        <section class="card">
          <h3>Últimos registros de IA (Auditoría del Perceptrón)</h3>
          @if (!logs().length) {
            <p class="muted">Sin registros todavía (la estrategia 1 offline no genera logs de LLM).</p>
          } @else {
            <div class="table-wrap">
              <table>
                <thead>
                  <tr><th>Fecha</th><th>Reunión</th><th>Etapa</th><th>Proveedor</th><th>Resultado</th><th>Latencia</th><th>VACA</th></tr>
                </thead>
                <tbody>
                  @for (l of logs(); track l.id) {
                    <tr>
                      <td class="small">{{ l.creado_en | date: 'short' }}</td>
                      <td class="small">{{ l.reunion_id }}</td>
                      <td>{{ l.etapa }}</td>
                      <td>{{ l.proveedor }}</td>
                      <td>{{ l.estado_binario === 0 ? '✅ Éxito' : '❌ Fallo' }}</td>
                      <td>{{ l.latencia_ms ?? '—' }} ms</td>
                      <td>{{ l.conmutacion_vaca ? 'Sí' : 'No' }}</td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </section>
      } @else if (!error()) {
        <div class="spinner"></div>
      }
    }

    <!-- SECCIÓN 2: CALIBRACIÓN WER & WER PONDERADO (MLOPS) -->
    @if (seccionActiva() === 'calibracion') {
      <section class="card">
        <div class="row-between">
          <div>
            <h3>🎯 Calibración de Transcripción (WER / WER Ponderado)</h3>
            <p class="muted small">Alineación exacta Levenshtein palabra por palabra según fórmulas de Sprint 2 (Meta de Entrega: WER &lt; 10%).</p>
          </div>
          <button class="mini" (click)="precargarEjemploWER()">Cargar Caso de Demostración</button>
        </div>

        <div class="grid-2" style="margin-top: 12px;">
          <div>
            <label>Texto Ground Truth (Transcripción Humana Patrón de Oro):
              <textarea rows="4" [(ngModel)]="werInputRef" placeholder="Texto de referencia verificado..."></textarea>
            </label>
          </div>
          <div>
            <label>Texto Hipótesis (Salida de Whisper / ASR):
              <textarea rows="4" [(ngModel)]="werInputHyp" placeholder="Texto generado por el modelo..."></textarea>
            </label>
          </div>
        </div>

        <div style="margin-top: 10px; display: flex; gap: 10px; align-items: center;">
          <button class="primary" [disabled]="calculandoWer() || !werInputRef || !werInputHyp" (click)="ejecutarCalibracionWER()">
            {{ calculandoWer() ? 'Calculando Levenshtein…' : 'Ejecutar Calibración y Alineación' }}
          </button>
          <span class="small muted">Ponderación: Fechas/Números/Negaciones = 3.0 · Nombres = 2.0 · Verbos = 1.5</span>
        </div>

        @if (resultadoWer(); as r) {
          <div style="margin-top: 20px; border-top: 1px solid var(--border); padding-top: 16px;">
            <div class="stats">
              <div class="stat">
                <span>WER Clásico</span>
                <strong [style.color]="r.wer_porcentaje <= 10 ? 'var(--ok)' : r.wer_porcentaje <= 25 ? 'var(--warn)' : 'var(--bad)'">
                  {{ r.wer_porcentaje }}%
                </strong>
                <span class="small muted">{{ r.cumple_meta_sprint ? '✅ Cumple Meta (<10%)' : '⚠️ Supera umbral' }}</span>
              </div>
              <div class="stat">
                <span>WER Ponderado (WER_w)</span>
                <strong>{{ r.wer_ponderado_porcentaje }}%</strong>
                <span class="small muted">Crítico para fechas/nombres</span>
              </div>
              <div class="stat">
                <span>Precisión Palabra</span>
                <strong>{{ r.precision_palabra_porcentaje }}%</strong>
                <span class="small muted">{{ r.aciertos }} aciertos de {{ r.total_palabras_gt }}</span>
              </div>
              <div class="stat">
                <span>Longitud Relativa</span>
                <strong>{{ r.longitud_relativa | number:'1.2-2' }}</strong>
                <span class="small muted">{{ r.longitud_relativa > 1.15 ? 'Alucinaciones (I)' : r.longitud_relativa < 0.85 ? 'Omisiones (D)' : 'Equilibrado' }}</span>
              </div>
            </div>

            <div style="margin-top: 12px; display: flex; gap: 16px; flex-wrap: wrap; font-size: 13px;">
              <span><strong>Sustituciones (S):</strong> {{ r.sustituciones }}</span>
              <span><strong>Eliminaciones (D):</strong> {{ r.eliminaciones }}</span>
              <span><strong>Inserciones (I):</strong> {{ r.inserciones }}</span>
              <span><strong>Estado Global:</strong> <span class="badge {{ r.estado_calidad }}">{{ r.estado_calidad }}</span></span>
            </div>

            <!-- Visualizador de Alineación Token por Token -->
            <div style="margin-top: 16px;">
              <h4>Alineación Palabra por Palabra (Levenshtein Diff):</h4>
              <div class="diff-contenedor">
                @for (token of r.alineacion; track $index) {
                  <span class="token-chip {{ token.op }}" [title]="'Operación: ' + token.op + ' | Peso: ' + token.peso">
                    @if (token.op === 'MATCH') {
                      <span>{{ token.ref }}</span>
                    } @else if (token.op === 'SUBSTITUTION') {
                      <del>{{ token.ref }}</del> <ins>{{ token.hyp }}</ins>
                    } @else if (token.op === 'DELETION') {
                      <del>-{{ token.ref }}</del>
                    } @else if (token.op === 'INSERTION') {
                      <ins>+{{ token.hyp }}</ins>
                    }
                  </span>
                }
              </div>
            </div>
          </div>
        }
      </section>
    }

    <!-- SECCIÓN 3: DATA DRIFT LÉXICO (OUT-OF-VOCABULARY) -->
    @if (seccionActiva() === 'drift') {
      <section class="card">
        <h3>🌊 Detección de Data Drift Lingüístico</h3>
        <p class="muted small">Monitorea cambios en el vocabulario, modismos colombianos no catalogados ("camello", "hacer la vuelta", etc.) y jerga técnica.</p>

        <label style="margin-top: 12px;">Texto a Analizar para Detección Léxica:
          <textarea rows="4" [(ngModel)]="driftInputTexto" placeholder="Pegue la transcripción o conversación a evaluar..."></textarea>
        </label>

        <div style="display: flex; gap: 10px; align-items: center; margin-top: 8px;">
          <button class="primary" [disabled]="analizandoDrift() || !driftInputTexto" (click)="ejecutarDataDrift()">
            {{ analizandoDrift() ? 'Analizando léxico…' : 'Evaluar Data Drift' }}
          </button>
          <button class="mini" (click)="precargarEjemploDrift()">Cargar Audio Coloquial Colombiano</button>
        </div>

        @if (resultadoDrift(); as d) {
          <div style="margin-top: 20px; border-top: 1px solid var(--border); padding-top: 16px;">
            <div class="stats">
              <div class="stat">
                <span>Ratio OOV (Desviación)</span>
                <strong [style.color]="d.ratio_oov_porcentaje < 15 ? 'var(--ok)' : d.ratio_oov_porcentaje < 30 ? 'var(--warn)' : 'var(--bad)'">
                  {{ d.ratio_oov_porcentaje }}%
                </strong>
                <span class="small muted">{{ d.total_palabras_oov }} de {{ d.palabras_unicas_evaluadas }} palabras únicas</span>
              </div>
              <div class="stat">
                <span>Estado de Data Drift</span>
                <strong><span class="badge {{ d.estado_drift }}">{{ d.estado_drift }}</span></strong>
                <span class="small muted">{{ d.alerta_drift ? '🚨 Alerta activada' : '✅ Vocabulario estable' }}</span>
              </div>
              <div class="stat">
                <span>Vocabulario Base Indexado</span>
                <strong>{{ d.tamano_vocabulario_base }} términos</strong>
                <span class="small muted">Dominio Corporativo & Scrum</span>
              </div>
            </div>

            <div style="margin-top: 12px; padding: 12px; background: #f8fafc; border-radius: 8px; border: 1px solid var(--border);">
              <strong>Recomendación MLOps:</strong>
              <p style="margin: 4px 0 0 0;">{{ d.recomendacion }}</p>
            </div>

            @if (d.palabras_oov_detectadas.length > 0) {
              <div style="margin-top: 16px;">
                <h4>Términos Fuera de Vocabulario (OOV) Detectados:</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px;">
                  @for (w of d.palabras_oov_detectadas; track w) {
                    <span class="oov-tag">{{ w }}</span>
                  }
                </div>
              </div>
            }
          </div>
        }
      </section>
    }

    <!-- SECCIÓN 4: PROMPT REGISTRY & VERSIONADO -->
    @if (seccionActiva() === 'prompts') {
      <section class="card">
        <div class="row-between">
          <div>
            <h3>📜 Prompt Registry & Control de Versiones</h3>
            <p class="muted small">Catálogo inmutable de plantillas de prompts de extracción, hash MD5 de auditoría y activación dinámica en producción.</p>
          </div>
          <button class="mini" (click)="cargarPrompts()">Recargar Catálogo</button>
        </div>

        <div style="display: flex; flex-direction: column; gap: 14px; margin-top: 16px;">
          @for (p of prompts(); track p.id) {
            <div class="prompt-card" [class.activo]="p.es_activo">
              <div class="row-between">
                <div>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <strong>{{ p.nombre }}</strong>
                    <span class="badge" [class.COMPLETADO]="p.es_activo">{{ p.es_activo ? 'PRODUCCIÓN ACTIVA' : 'DISPONIBLE' }}</span>
                    <span class="small muted">v{{ p.version }}</span>
                  </div>
                  <p class="muted small" style="margin: 4px 0;">{{ p.descripcion }}</p>
                </div>
                <div>
                  @if (!p.es_activo) {
                    <button class="primary mini" (click)="activarPrompt(p.id)">Activar en Caliente</button>
                  } @else {
                    <span class="small" style="color: var(--ok); font-weight: bold;">En uso por VACAS</span>
                  }
                </div>
              </div>

              <div style="margin-top: 10px; font-size: 12px; display: flex; gap: 16px; flex-wrap: wrap; color: #4b5563;">
                <span><strong>ID:</strong> <code>{{ p.id }}</code></span>
                <span><strong>MD5 Hash:</strong> <code>{{ p.hash_md5 }}</code></span>
                <span><strong>Modelos:</strong> {{ p.modelos_compatibles.join(', ') }}</span>
              </div>
            </div>
          }
        </div>
      </section>
    }
  `,
  styles: [`
    .tabs-mlops {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }
    .tabs-mlops button {
      background: #e5e7eb;
      color: #374151;
      border: 1px solid transparent;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 13px;
    }
    .tabs-mlops button:hover {
      background: #d1d5db;
    }
    .tabs-mlops button.activo {
      background: var(--primary);
      color: #fff;
    }
    textarea {
      width: 100%;
      font-family: inherit;
      padding: 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      box-sizing: border-box;
      resize: vertical;
    }
    .diff-contenedor {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 12px;
      background: #f8fafc;
      border-radius: 8px;
      border: 1px solid var(--border);
      max-height: 220px;
      overflow-y: auto;
    }
    .token-chip {
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 13px;
      font-family: monospace;
    }
    .token-chip.MATCH {
      background: #dcfce7;
      color: #166534;
    }
    .token-chip.SUBSTITUTION {
      background: #fee2e2;
      color: #991b1b;
      font-weight: bold;
    }
    .token-chip.DELETION {
      background: #fef3c7;
      color: #92400e;
    }
    .token-chip.INSERTION {
      background: #f3e8ff;
      color: #6b21a8;
    }
    .oov-tag {
      background: #fee2e2;
      color: #991b1b;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-family: monospace;
    }
    .prompt-card {
      padding: 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #fff;
      transition: all .15s ease;
    }
    .prompt-card.activo {
      border-left: 5px solid var(--primary);
      background: #faf5ff;
    }
  `]
})
export class AuditoriaComponent implements OnInit {
  api = inject(ApiService);

  seccionActiva = signal<'telemetria' | 'calibracion' | 'drift' | 'prompts'>('telemetria');
  estado = signal<EstadoAuditoria | null>(null);
  metricas = signal<Metricas | null>(null);
  logs = signal<LogIA[]>([]);
  cache = signal<EstadoCache | null>(null);
  prompts = signal<PromptVersion[]>([]);
  msg = signal('');
  error = signal('');

  // Estados Calibración WER
  werInputRef = '';
  werInputHyp = '';
  calculandoWer = signal(false);
  resultadoWer = signal<CalibrarWER | null>(null);

  // Estados Data Drift
  driftInputTexto = '';
  analizandoDrift = signal(false);
  resultadoDrift = signal<DataDrift | null>(null);

  ngOnInit() {
    this.cargar();
    this.cargarPrompts();
  }

  cargar() {
    forkJoin([this.api.estadoAuditoria(), this.api.metricas(), this.api.logs(), this.api.estadoCache()]).subscribe({
      next: ([e, m, l, c]) => {
        this.estado.set(e.data);
        this.metricas.set(m.data);
        this.logs.set(l.data);
        this.cache.set(c.data);
      },
      error: (err: Error) => this.error.set(err.message),
    });
  }

  cargarPrompts() {
    this.api.listarPrompts().subscribe({
      next: (res) => this.prompts.set(res.data),
      error: () => {}
    });
  }

  activarPrompt(versionId: string) {
    this.api.activarPrompt(versionId).subscribe({
      next: (res) => {
        this.msg.set(`Prompt activado en caliente: ${res.data.nombre}`);
        this.cargarPrompts();
      },
      error: (e: Error) => this.error.set(e.message)
    });
  }

  precargarEjemploWER() {
    this.werInputRef = 'Juan Pérez debe entregar el informe de métricas de rendimiento este viernes 20 de octubre. Carlos acordó revisar los endpoints del backend mañana a primera hora.';
    this.werInputHyp = 'Juan Pérez debe entregar el informe de métricas de rendimiento este lunes 20 de octubre. Carlos acordó revisar los endpoints del backend mañana a primera hora.';
  }

  ejecutarCalibracionWER() {
    if (!this.werInputRef || !this.werInputHyp) return;
    this.calculandoWer.set(true);
    this.api.calibrarWER({
      texto_referencia: this.werInputRef,
      texto_hipotesis: this.werInputHyp,
      modelo_evaluado: 'whisper-medium'
    }).subscribe({
      next: (res) => {
        this.calculandoWer.set(false);
        this.resultadoWer.set(res.data);
      },
      error: (err: Error) => {
        this.calculandoWer.set(false);
        this.error.set(err.message);
      }
    });
  }

  precargarEjemploDrift() {
    this.driftInputTexto = 'Oigan equipo, el camello de la entrega está re tenaz pero toca hacer la vuelta hoy mismo para no quedar colgados con el parche.';
  }

  ejecutarDataDrift() {
    if (!this.driftInputTexto) return;
    this.analizandoDrift.set(true);
    this.api.analizarDataDrift({ texto: this.driftInputTexto }).subscribe({
      next: (res) => {
        this.analizandoDrift.set(false);
        this.resultadoDrift.set(res.data);
      },
      error: (err: Error) => {
        this.analizandoDrift.set(false);
        this.error.set(err.message);
      }
    });
  }

  accion(obs: Observable<ResponseDto<unknown>>) {
    this.error.set('');
    obs.subscribe({
      next: (r) => {
        this.msg.set(r.message);
        this.cargar();
      },
      error: (e: Error) => this.error.set(e.message),
    });
  }
}
