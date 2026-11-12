import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { ReunionResumen } from '../core/models';

@Component({
  selector: 'app-historial',
  imports: [RouterLink],
  template: `
    @if (error()) {
      <p class="error">{{ error() }}</p>
    } @else if (!reuniones()) {
      <div class="spinner"></div>
    } @else {
      <section class="card">
        <h2>Historial de reuniones</h2>
        @if (msg()) { <p class="success">{{ msg() }}</p> }
        @if (!reuniones()!.length) {
          <p class="muted">Aún no hay reuniones. Sube la primera desde “Subir reunión”.</p>
        }
        <div class="lista">
          @for (r of reuniones(); track r.id_reunion) {
            <a class="item" [routerLink]="['/minuta', r.id_reunion]">
              <div class="row-between">
                <strong>{{ r.nombre_archivo }}</strong>
                <div style="display: flex; align-items: center; gap: 8px;">
                  @if (r.estado === 'EN_COLA' || r.estado === 'PROCESANDO') {
                    <button class="danger mini" (click)="detener($event, r.id_reunion)">⏹ Detener</button>
                  }
                  <span [class]="'badge ' + r.estado">{{ r.estado }}</span>
                  <button
                    class="danger mini"
                    [disabled]="eliminandoId() === r.id_reunion"
                    (click)="eliminar($event, r)"
                    title="Eliminar registro y todos sus datos asociados en cascada">
                    {{ eliminandoId() === r.id_reunion ? 'Eliminando…' : '🗑️ Eliminar' }}
                  </button>
                </div>
              </div>
              <span class="muted small">{{ r.id_reunion }} · {{ r.total_acuerdos }} acuerdo(s)</span>
              @if (r.resumen_ejecutivo) { <p class="extracto">{{ r.resumen_ejecutivo }}</p> }
            </a>
          }
        </div>
      </section>
    }
  `,
})
export class HistorialComponent implements OnInit {
  private api = inject(ApiService);
  reuniones = signal<ReunionResumen[] | null>(null);
  eliminandoId = signal<string | null>(null);
  msg = signal('');
  error = signal('');

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.api.listarReuniones().subscribe({
      next: (r) => this.reuniones.set(r.data),
      error: (e: Error) => this.error.set(e.message),
    });
  }

  detener(event: MouseEvent, id: string) {
    event.preventDefault();
    event.stopPropagation();
    this.api.cancelarReunion(id).subscribe({
      next: () => this.cargar(),
      error: (e: Error) => this.error.set(e.message),
    });
  }

  eliminar(event: MouseEvent, r: ReunionResumen) {
    event.preventDefault();
    event.stopPropagation();
    const ok = confirm(
      `¿Eliminar permanentemente "${r.nombre_archivo}" (${r.id_reunion})?\n\n` +
      `Esta acción eliminará en cascada la reunión, sus ${r.total_acuerdos} acuerdo(s), historial, logs de auditoría IA, alertas y archivos temporales.`
    );
    if (!ok) return;

    this.error.set('');
    this.msg.set('');
    this.eliminandoId.set(r.id_reunion);
    this.api.eliminarReunion(r.id_reunion).subscribe({
      next: (res) => {
        this.eliminandoId.set(null);
        this.msg.set(res.message);
        this.reuniones.update((list) => (list ? list.filter((item) => item.id_reunion !== r.id_reunion) : list));
      },
      error: (e: Error) => {
        this.eliminandoId.set(null);
        this.error.set(e.message);
      },
    });
  }
}
