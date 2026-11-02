import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';
import { ApiService } from '../core/api.service';
import { Responsable } from '../core/models';

@Component({
  selector: 'app-equipo',
  imports: [FormsModule],
  template: `
    <section class="grid-2">
      <div class="card">
        <h2>Miembros del equipo</h2>
        <p class="muted">La IA usa estos nombres y apodos para asignar responsables (Fuzzy Matching).</p>
        @if (!miembros()) {
          <div class="spinner"></div>
        } @else {
          <div class="lista">
            @for (m of miembros(); track m.id) {
              <div class="item static">
                <div class="row-between">
                  <strong>{{ m.nombre_completo }}</strong>
                  <span class="muted small">{{ m.rol }}</span>
                </div>
                <span class="muted small">{{ m.email }}</span>
                <div class="chips">
                  @for (a of m.alias_conocidos; track a) { <span class="chip">{{ a }}</span> }
                </div>
              </div>
            }
          </div>
        }
      </div>

      <form class="card" #f="ngForm" (ngSubmit)="guardar(f)">
        <h2>Registrar integrante</h2>
        <label>Nombre completo *
          <input name="nombre" required [(ngModel)]="form.nombre" placeholder="Andrés Morales" />
        </label>
        <label>Alias / apodos (separados por coma)
          <input name="alias" [(ngModel)]="form.alias" placeholder="Andy, Morales, Andres" />
        </label>
        <label>Email
          <input name="email" type="email" email [(ngModel)]="form.email" placeholder="andres@empresa.com" />
        </label>
        <label>Rol
          <input name="rol" [(ngModel)]="form.rol" placeholder="DevOps Engineer" />
        </label>
        @if (error()) { <p class="error">{{ error() }}</p> }
        @if (ok()) { <p class="success">{{ ok() }}</p> }
        <button class="primary block" type="submit" [disabled]="f.invalid">Guardar</button>
      </form>
    </section>
  `,
})
export class EquipoComponent implements OnInit {
  private api = inject(ApiService);
  miembros = signal<Responsable[] | null>(null);
  error = signal('');
  ok = signal('');
  form = { nombre: '', alias: '', email: '', rol: '' };

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.api.listarResponsables().subscribe({
      next: (r) => this.miembros.set(r.data),
      error: (e: Error) => this.error.set(e.message),
    });
  }

  guardar(f: NgForm) {
    this.error.set('');
    this.ok.set('');
    this.api.crearResponsable({
      nombre_completo: this.form.nombre.trim(),
      alias_conocidos: this.form.alias.split(',').map((s) => s.trim()).filter(Boolean),
      email: this.form.email.trim() || null,
      rol: this.form.rol.trim() || null,
    }).subscribe({
      next: (res) => {
        this.ok.set(res.message);
        f.resetForm();
        this.form = { nombre: '', alias: '', email: '', rol: '' };
        this.cargar();
      },
      error: (e: Error) => this.error.set(e.message),
    });
  }
}
