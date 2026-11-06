import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { DatePipe } from '@angular/common';
import { ApiService } from './core/api.service';
import { AlertaSistema } from './core/models';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, DatePipe],
  template: `
    <header class="topbar">
      <div class="brand">
        <span class="logo">🎙️</span>
        <div>
          <strong>Transcriptor Maestro</strong>
          <small>Seguimiento de acuerdos de reuniones · MLOps Enterprise</small>
        </div>
      </div>
      <nav>
        @for (t of tabs; track t.path) {
          <a class="tab" [routerLink]="t.path" routerLinkActive="active">{{ t.label }}</a>
        }
      </nav>

      <div class="header-actions">
        <!-- Botón y Campana de Alertas del Sistema (Curva de Espacios Iguales) -->
        <button class="btn-alertas" (click)="toggleAlertas()" title="Centro de Notificaciones y Alertas">
          <span class="campana-icono">🔔</span>
          <span class="alertas-texto">Alertas</span>
          @if (alertas().length > 0) {
            <span class="badge-contador">{{ alertas().length }}</span>
          }
        </button>

        <span class="status" [class.ok]="online() === true" [class.off]="online() === false">
          {{ online() === null ? 'Conectando…' : online() ? 'API en línea' : 'API desconectada' }}
        </span>
      </div>
    </header>

    <!-- Panel Flotante / Drawer de Alertas del Sistema -->
    @if (modalAlertasAbierto()) {
      <div class="alertas-overlay" (click)="toggleAlertas()">
        <div class="alertas-panel" (click)="$event.stopPropagation()">
          <div class="alertas-header">
            <h3>🔔 Notificaciones del Sistema</h3>
            <button class="mini link" (click)="toggleAlertas()">✕ Cerrar</button>
          </div>

          <div class="alertas-actions-bar">
            <button class="primary mini" [disabled]="ejecutandoBarrido()" (click)="ejecutarBarrido()">
              {{ ejecutandoBarrido() ? 'Ejecutando barrido…' : '⚡ Ejecutar Curva Espacios Iguales' }}
            </button>
            <span class="muted small">{{ alertas().length }} activa(s)</span>
          </div>

          @if (mensajeBarrido()) {
            <p class="success small">{{ mensajeBarrido() }}</p>
          }

          <div class="alertas-lista">
            @if (alertas().length === 0) {
              <p class="muted center" style="padding: 24px;">No hay alertas pendientes en el sistema. Todos los compromisos al día.</p>
            } @else {
              @for (a of alertas(); track a.id) {
                <div class="alerta-item" [class.critica]="a.severidad === 'CRITICAL'" [class.warning]="a.severidad === 'WARNING'">
                  <div class="alerta-top">
                    <span class="alerta-tipo">{{ a.tipo_alerta }}</span>
                    <span class="alerta-sev {{ a.severidad }}">{{ a.severidad }}</span>
                    <button class="mini link marcar-btn" (click)="marcarLeida(a.id)">Marcar leída</button>
                  </div>
                  <p class="alerta-msg">{{ a.mensaje }}</p>
                  <span class="alerta-fecha">{{ a.creado_en | date:'short' }}</span>
                </div>
              }
            }
          </div>
        </div>
      </div>
    }

    <main>
      <router-outlet />
    </main>
  `,
  styles: [`
    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .btn-alertas {
      background: #1f2937;
      color: #fff;
      border: 1px solid #374151;
      padding: 6px 12px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      position: relative;
    }
    .btn-alertas:hover {
      background: #374151;
      border-color: #4b5563;
    }
    .badge-contador {
      background: #dc2626;
      color: #fff;
      font-size: 11px;
      font-weight: bold;
      padding: 1px 6px;
      border-radius: 999px;
    }
    .alertas-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.4);
      z-index: 100;
      display: flex;
      justify-content: flex-end;
    }
    .alertas-panel {
      width: 420px;
      max-width: 90vw;
      background: #fff;
      height: 100%;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.15);
      display: flex;
      flex-direction: column;
      padding: 16px;
      box-sizing: border-box;
      color: #111827;
    }
    .alertas-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #e5e7eb;
      padding-bottom: 10px;
    }
    .alertas-actions-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid #f3f4f6;
    }
    .alertas-lista {
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 10px;
    }
    .alerta-item {
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid #e5e7eb;
      background: #f9fafb;
      font-size: 13px;
    }
    .alerta-item.critica {
      border-left: 4px solid #dc2626;
      background: #fef2f2;
    }
    .alerta-item.warning {
      border-left: 4px solid #ca8a04;
      background: #fefce8;
    }
    .alerta-top {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
    }
    .alerta-tipo {
      font-weight: 700;
      font-size: 12px;
    }
    .alerta-sev {
      font-size: 10px;
      font-weight: bold;
      padding: 1px 5px;
      border-radius: 4px;
    }
    .alerta-sev.CRITICAL { background: #fee2e2; color: #991b1b; }
    .alerta-sev.WARNING { background: #fef9c3; color: #854d0e; }
    .marcar-btn { margin-left: auto; }
    .alerta-msg { margin: 4px 0; line-height: 1.4; }
    .alerta-fecha { font-size: 11px; color: #6b7280; }
  `]
})
export class AppComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);
  online = signal<boolean | null>(null);
  alertas = signal<AlertaSistema[]>([]);
  modalAlertasAbierto = signal(false);
  ejecutandoBarrido = signal(false);
  mensajeBarrido = signal('');
  private timer?: ReturnType<typeof setInterval>;

  tabs = [
    { path: '/subir', label: 'Subir reunión' },
    { path: '/historial', label: 'Historial' },
    { path: '/acuerdos', label: 'Acuerdos' },
    { path: '/equipo', label: 'Equipo' },
    { path: '/auditoria', label: 'Auditoría MLOps' },
  ];

  ngOnInit() {
    this.check();
    this.cargarAlertas();
    this.timer = setInterval(() => {
      this.check();
      this.cargarAlertas();
    }, 15000);
  }

  ngOnDestroy() {
    clearInterval(this.timer);
  }

  toggleAlertas() {
    this.modalAlertasAbierto.update(v => !v);
    if (this.modalAlertasAbierto()) {
      this.cargarAlertas();
    }
  }

  cargarAlertas() {
    this.api.listarAlertas(true).subscribe({
      next: (res) => this.alertas.set(res.data),
      error: () => {}
    });
  }

  marcarLeida(id: string) {
    this.api.marcarAlertaLeida(id).subscribe({
      next: () => {
        this.alertas.update(list => list.filter(a => a.id !== id));
      }
    });
  }

  ejecutarBarrido() {
    this.ejecutandoBarrido.set(true);
    this.mensajeBarrido.set('');
    this.api.ejecutarBarridoScheduler().subscribe({
      next: (res) => {
        this.ejecutandoBarrido.set(false);
        this.mensajeBarrido.set(`Barrido finalizado: ${res.data.acuerdos_atrasados} atrasados, ${res.data.omisiones_detectadas} omisiones detectadas.`);
        this.cargarAlertas();
      },
      error: (err: Error) => {
        this.ejecutandoBarrido.set(false);
        this.mensajeBarrido.set(`Error: ${err.message}`);
      }
    });
  }

  private check() {
    this.api.health().subscribe({
      next: () => this.online.set(true),
      error: () => this.online.set(false),
    });
  }
}
