import { Component, inject, input, output, signal } from '@angular/core';
import { ApiService } from '../core/api.service';
import { Acuerdo, ESTADOS_ACUERDO, EstadoAcuerdo } from '../core/models';
import { FuzzyBadgeComponent } from './fuzzy-badge.component';

@Component({
  selector: 'app-tabla-acuerdos',
  imports: [FuzzyBadgeComponent],
  template: `
    @if (!acuerdos().length) {
      <p class="muted">No se detectaron acuerdos.</p>
    } @else {
      <div class="table-wrap">
        @if (error()) { <p class="error">{{ error() }}</p> }
        <table>
          <thead>
            <tr><th>Tarea</th><th>Responsable</th><th>Fecha límite</th><th>Estado</th><th></th></tr>
          </thead>
          <tbody>
            @for (a of acuerdos(); track a.id_acuerdo) {
              <tr>
                <td>{{ a.tarea_desc }}</td>
                <td>
                  {{ a.responsable }} <app-fuzzy [valor]="a.similitud_fuzzy" />
                  @if (a.responsable_crudo && a.responsable_crudo !== a.responsable) {
                    <div class="muted small">dicho como “{{ a.responsable_crudo }}”</div>
                  }
                </td>
                <td>{{ a.fecha_compromiso || '—' }}</td>
                <td>
                  <select [class]="'estado ' + a.estado" [value]="a.estado"
                          (change)="cambiar(a.id_acuerdo, $any($event.target).value)">
                    @for (s of estados; track s) { <option [value]="s" [selected]="s === a.estado">{{ s }}</option> }
                  </select>
                </td>
                <td>
                  <button class="link" (click)="abierto.set(abierto() === a.id_acuerdo ? null : a.id_acuerdo)">
                    {{ abierto() === a.id_acuerdo ? 'Ocultar cita' : 'Ver cita textual' }}
                  </button>
                </td>
              </tr>
              @if (abierto() === a.id_acuerdo) {
                <tr class="cita"><td colspan="5"><blockquote>“{{ a.fragmento_original }}”</blockquote></td></tr>
              }
            }
          </tbody>
        </table>
      </div>
    }
  `,
})
export class TablaAcuerdosComponent {
  private api = inject(ApiService);
  acuerdos = input.required<Acuerdo[]>();
  cambio = output<void>();
  estados = ESTADOS_ACUERDO;
  abierto = signal<string | null>(null);
  error = signal('');

  cambiar(id: string, estado: EstadoAcuerdo) {
    this.error.set('');
    this.api.cambiarEstadoAcuerdo(id, estado).subscribe({
      next: () => this.cambio.emit(),
      error: (e: Error) => this.error.set(e.message),
    });
  }
}
