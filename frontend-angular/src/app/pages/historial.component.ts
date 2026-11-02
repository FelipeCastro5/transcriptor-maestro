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
        @if (!reuniones()!.length) {
          <p class="muted">Aún no hay reuniones. Sube la primera desde “Subir reunión”.</p>
        }
        <div class="lista">
          @for (r of reuniones(); track r.id_reunion) {
            <a class="item" [routerLink]="['/minuta', r.id_reunion]">
              <div class="row-between">
                <strong>{{ r.nombre_archivo }}</strong>
                <span [class]="'badge ' + r.estado">{{ r.estado }}</span>
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
  error = signal('');

  ngOnInit() {
    this.api.listarReuniones().subscribe({
      next: (r) => this.reuniones.set(r.data),
      error: (e: Error) => this.error.set(e.message),
    });
  }
}
