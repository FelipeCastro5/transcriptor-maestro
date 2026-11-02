import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { ApiService } from '../core/api.service';
import { Acuerdo, ESTADOS_ACUERDO, EstadoAcuerdo } from '../core/models';
import { FuzzyBadgeComponent } from '../shared/fuzzy-badge.component';

@Component({
  selector: 'app-acuerdos',
  imports: [RouterLink, FuzzyBadgeComponent],
  template: `
    @if (error()) { <p class="error">{{ error() }}</p> }
    @if (!acuerdos()) {
      <div class="spinner"></div>
    } @else {
      <p class="muted">Arrastra las tarjetas entre columnas o usa los botones para cambiar el estado.</p>
      <div class="kanban">
        @for (estado of estados; track estado) {
          <div class="columna" [class.sobre]="sobre() === estado"
               (dragover)="$event.preventDefault(); sobre.set(estado)"
               (dragleave)="sobre.set(null)"
               (drop)="soltar($event, estado)">
            <h3>{{ titulos[estado] }} <span class="muted">({{ de(estado).length }})</span></h3>
            @for (a of de(estado); track a.id_acuerdo) {
              <div class="tarjeta" draggable="true" (dragstart)="$event.dataTransfer?.setData('id', a.id_acuerdo)">
                <strong>{{ a.tarea_desc }}</strong>
                <span>{{ a.responsable }} <app-fuzzy [valor]="a.similitud_fuzzy" /></span>
                <span class="muted small">
                  {{ a.fecha_compromiso || 'Sin fecha' }} ·
                  <a [routerLink]="['/minuta', a.id_reunion]">{{ a.id_reunion }}</a>
                </span>
                <div class="acciones">
                  @for (s of estados; track s) {
                    @if (s !== estado) {
                      <button class="mini" (click)="mover(a.id_acuerdo, s)">→ {{ s }}</button>
                    }
                  }
                </div>
              </div>
            }
          </div>
        }
      </div>
    }
  `,
})
export class AcuerdosComponent implements OnInit {
  private api = inject(ApiService);
  estados = ESTADOS_ACUERDO;
  titulos: Record<EstadoAcuerdo, string> = {
    pendiente: '🟡 Pendiente',
    completado: '🟢 Completado',
    atrasado: '🔴 Atrasado',
  };
  acuerdos = signal<Acuerdo[] | null>(null);
  sobre = signal<EstadoAcuerdo | null>(null);
  error = signal('');

  ngOnInit() {
    this.cargar();
  }

  de(estado: EstadoAcuerdo) {
    return (this.acuerdos() ?? []).filter((a) => a.estado === estado);
  }

  cargar() {
    this.api.listarAcuerdos().subscribe({
      next: (r) => this.acuerdos.set(r.data),
      error: (e: Error) => this.error.set(e.message),
    });
  }

  soltar(e: DragEvent, estado: EstadoAcuerdo) {
    e.preventDefault();
    this.sobre.set(null);
    const id = e.dataTransfer?.getData('id');
    if (id) this.mover(id, estado);
  }

  mover(id: string, estado: EstadoAcuerdo) {
    const actual = this.acuerdos()?.find((a) => a.id_acuerdo === id);
    if (!actual || actual.estado === estado) return;
    this.api.cambiarEstadoAcuerdo(id, estado, 'Movido desde el tablero').subscribe({
      next: () => this.cargar(),
      error: (e: Error) => this.error.set(e.message),
    });
  }
}
