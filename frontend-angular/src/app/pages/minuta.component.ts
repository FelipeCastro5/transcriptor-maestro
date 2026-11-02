import { Component, OnInit, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { ReunionDetalle } from '../core/models';
import { TablaAcuerdosComponent } from '../shared/tabla-acuerdos.component';

@Component({
  selector: 'app-minuta',
  imports: [RouterLink, TablaAcuerdosComponent],
  template: `
    @if (error()) {
      <section class="card"><p class="error">{{ error() }}</p><a routerLink="/historial">← Historial</a></section>
    } @else if (!det()) {
      <div class="spinner"></div>
    } @else {
      @let d = det()!;
      <section class="card">
        <a class="link" routerLink="/historial">← Historial</a>
        <div class="row-between">
          <div>
            <h2>{{ d.nombre_archivo }}</h2>
            <p class="muted">
              {{ d.id_reunion }} · Estrategia {{ d.estrategia_utilizada ?? '—' }} · {{ d.tiempo_procesamiento_seg ?? '—' }} s de cómputo
            </p>
          </div>
          <span [class]="'badge ' + d.estado">{{ d.estado }}</span>
        </div>
        @if (d.error_detalle) { <p class="error">{{ d.error_detalle }}</p> }
      </section>

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
    }
  `,
})
export class MinutaComponent implements OnInit {
  private api = inject(ApiService);
  id = input.required<string>(); // viene del parámetro de ruta :id
  det = signal<ReunionDetalle | null>(null);
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
}
