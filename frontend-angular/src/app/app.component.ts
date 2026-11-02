import { Component, OnDestroy, OnInit, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ApiService } from './core/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <header class="topbar">
      <div class="brand">
        <span class="logo">🎙️</span>
        <div>
          <strong>Transcriptor Maestro</strong>
          <small>Seguimiento de acuerdos de reuniones · Angular</small>
        </div>
      </div>
      <nav>
        @for (t of tabs; track t.path) {
          <a class="tab" [routerLink]="t.path" routerLinkActive="active">{{ t.label }}</a>
        }
      </nav>
      <span class="status" [class.ok]="online() === true" [class.off]="online() === false">
        {{ online() === null ? 'Conectando…' : online() ? 'API en línea' : 'API desconectada' }}
      </span>
    </header>
    <main>
      <router-outlet />
    </main>
  `,
})
export class AppComponent implements OnInit, OnDestroy {
  private api = inject(ApiService);
  online = signal<boolean | null>(null);
  private timer?: ReturnType<typeof setInterval>;

  tabs = [
    { path: '/subir', label: 'Subir reunión' },
    { path: '/historial', label: 'Historial' },
    { path: '/acuerdos', label: 'Acuerdos' },
    { path: '/equipo', label: 'Equipo' },
    { path: '/auditoria', label: 'Auditoría' },
  ];

  ngOnInit() {
    this.check();
    this.timer = setInterval(() => this.check(), 15000);
  }

  ngOnDestroy() {
    clearInterval(this.timer);
  }

  private check() {
    this.api.health().subscribe({
      next: () => this.online.set(true),
      error: () => this.online.set(false),
    });
  }
}
