import { Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Observable, forkJoin } from 'rxjs';
import { ApiService } from '../core/api.service';
import { EstadoAuditoria, EstadoCache, LogIA, Metricas, ResponseDto } from '../core/models';

@Component({
  selector: 'app-auditoria',
  imports: [DatePipe],
  template: `
    @if (msg()) { <p class="success">{{ msg() }}</p> }
    @if (error()) { <p class="error">{{ error() }}</p> }
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
            {{ e.simulacion_fallo_activa ? 'Desactivar simulación de caída' : 'Simular caída del LLM primario' }}
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
        <h3>Últimos registros de IA</h3>
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
  `,
})
export class AuditoriaComponent implements OnInit {
  api = inject(ApiService);
  estado = signal<EstadoAuditoria | null>(null);
  metricas = signal<Metricas | null>(null);
  logs = signal<LogIA[]>([]);
  cache = signal<EstadoCache | null>(null);
  msg = signal('');
  error = signal('');

  ngOnInit() {
    this.cargar();
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
