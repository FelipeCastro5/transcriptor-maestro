import { Component, OnDestroy, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Subscription, interval, switchMap } from 'rxjs';
import { ApiService } from '../core/api.service';
import { ConfigIA, EstadoReunion } from '../core/models';

interface Proceso {
  id: string;
  estado: EstadoReunion;
  progreso: string | null;
  error?: string | null;
}

@Component({
  selector: 'app-subir',
  imports: [FormsModule],
  template: `
    @if (proceso(); as p) {
      <section class="card center">
        @if (p.estado === 'EN_COLA' || p.estado === 'PROCESANDO') {
          <div class="spinner"></div>
        }
        <h2>
          {{ p.estado === 'FALLIDO' ? 'El procesamiento falló' : p.estado === 'CANCELADO' ? 'Procesamiento cancelado' : 'Procesando reunión…' }}
        </h2>
        <p class="muted">{{ p.id }}</p>
        <span [class]="'badge ' + p.estado">{{ p.estado }}</span>
        <p>{{ p.progreso }}</p>
        @if (p.error && p.estado !== 'CANCELADO') { <p class="error">{{ p.error }}</p> }
        @if (error()) { <p class="error">{{ error() }}</p> }
        <div style="display: flex; gap: 10px; margin-top: 8px; flex-wrap: wrap; justify-content: center;">
          @if (p.estado === 'EN_COLA' || p.estado === 'PROCESANDO') {
            <button class="danger" [disabled]="cancelando()" (click)="detener()">
              {{ cancelando() ? 'Cancelando…' : '⏹ Detener procesamiento' }}
            </button>
          }
          @if (p.estado === 'FALLIDO' || p.estado === 'CANCELADO') {
            <button class="primary" (click)="reiniciar()">Subir otro archivo / Intentar de nuevo</button>
          }
        </div>
      </section>
    } @else {
      <section class="grid-2">
        <div class="card">
          <h2>1. Archivo de la reunión</h2>
          <div class="dropzone" [class.drag]="drag()"
               (click)="input.click()"
               (dragover)="$event.preventDefault(); drag.set(true)"
               (dragleave)="drag.set(false)"
               (drop)="soltar($event)">
            <input #input type="file" [accept]="extensiones" hidden (change)="elegir($any($event.target).files[0])" />
            @if (file(); as f) {
              <strong>{{ f.name }}</strong>
              <span class="muted">{{ (f.size / 1024 / 1024).toFixed(2) }} MB · clic para cambiar</span>
            } @else {
              <strong>Arrastra un audio aquí o haz clic</strong>
              <span class="muted">.mp3 .wav .m4a .flac .ogg — o un .txt con la transcripción</span>
            }
          </div>
          @if (error()) { <p class="error">{{ error() }}</p> }
          <button class="primary block" [disabled]="!file() || enviando()" (click)="enviar()">
            {{ enviando() ? 'Enviando…' : 'Procesar reunión' }}
          </button>
        </div>

        <div class="card">
          <h2>2. Configuración de IA</h2>
          <label>Estrategia
            <select [(ngModel)]="config.estrategia">
              @for (e of estrategias; track e.value) { <option [ngValue]="e.value">{{ e.label }}</option> }
            </select>
          </label>
          <label>Modelo Whisper
            <select [(ngModel)]="config.modelo_whisper">
              <option value="small">small (rápido)</option>
              <option value="medium">medium (por defecto)</option>
              <option value="large">large (máxima precisión)</option>
            </select>
          </label>
          <label>Proveedor LLM
            <select [(ngModel)]="config.llm_preferido">
              <option value="deepseek">DeepSeek</option>
              <option value="openai">OpenAI</option>
            </select>
          </label>
          <label>Modelo LLM
            <input [(ngModel)]="config.modelo_llm" />
          </label>
          <div style="margin-top: 14px; padding: 12px; background: #f8fafc; border: 1px solid var(--border); border-radius: 8px;">
            <label style="display: flex; flex-direction: row; align-items: center; gap: 8px; margin: 0; cursor: pointer;">
              <input type="checkbox" [(ngModel)]="config.modo_consenso" style="width: auto; cursor: pointer;" />
              <span><strong>Modo Consenso Dual (DeepSeek + OpenAI)</strong></span>
            </label>
            <p class="hint" style="margin-top: 6px;">
              Invocación concurrente en paralelo con cálculo de discrepancia entre modelos (&le;20%) y verificación cruzada en tiempo real.
            </p>
          </div>
          <p class="hint">Las estrategias 2–5 usan las API keys de <code>backend/.env</code>. Sin keys, usa la estrategia 1.</p>
        </div>
      </section>
    }
  `,
})
export class SubirComponent implements OnDestroy {
  private api = inject(ApiService);
  private router = inject(Router);
  private polling?: Subscription;

  extensiones = '.mp3,.wav,.m4a,.flac,.ogg,.txt';
  estrategias = [
    { value: 5, label: '5 · Híbrido maduro con failover VACAS (recomendado)' },
    { value: 4, label: '4 · Prompt avanzado (lenguaje informal)' },
    { value: 3, label: '3 · Whisper + prompt elemental' },
    { value: 2, label: '2 · Chunking 30s Hugging Face' },
    { value: 1, label: '1 · Reglas offline (sin LLM)' },
  ];
  config: ConfigIA = { estrategia: 5, modelo_whisper: 'medium', llm_preferido: 'deepseek', modelo_llm: 'deepseek-chat', modo_consenso: false };

  file = signal<File | null>(null);
  drag = signal(false);
  enviando = signal(false);
  cancelando = signal(false);
  proceso = signal<Proceso | null>(null);
  error = signal('');

  ngOnDestroy() {
    this.polling?.unsubscribe();
  }

  elegir(f?: File) {
    if (f) {
      this.file.set(f);
      this.error.set('');
    }
  }

  soltar(e: DragEvent) {
    e.preventDefault();
    this.drag.set(false);
    this.elegir(e.dataTransfer?.files[0]);
  }

  enviar() {
    const f = this.file();
    if (!f) return;
    this.error.set('');
    this.enviando.set(true);
    this.api.subirAudio(f, this.config).subscribe({
      next: (res) => {
        this.enviando.set(false);
        const id = res.data.id_reunion;
        this.proceso.set({ id, estado: res.data.estado, progreso: res.message });
        this.iniciarPolling(id);
      },
      error: (e: Error) => {
        this.enviando.set(false);
        this.error.set(e.message);
      },
    });
  }

  // Polling cada 2.5 s, según FRONTEND_HANDOFF.md
  private iniciarPolling(id: string) {
    this.polling = interval(2500)
      .pipe(switchMap(() => this.api.estadoReunion(id)))
      .subscribe({
        next: ({ data }) => {
          this.proceso.set({ id, estado: data.estado, progreso: data.progreso_estimado, error: data.error_detalle });
          if (data.estado === 'COMPLETADO') {
            this.polling?.unsubscribe();
            this.router.navigate(['/minuta', id]);
          }
          if (data.estado === 'FALLIDO' || data.estado === 'CANCELADO') {
            this.polling?.unsubscribe();
          }
        },
        error: (e: Error) => this.error.set(e.message),
      });
  }

  detener() {
    const p = this.proceso();
    if (!p || this.cancelando()) return;
    this.cancelando.set(true);
    this.error.set('');
    this.polling?.unsubscribe();
    this.api.cancelarReunion(p.id).subscribe({
      next: ({ data }) => {
        this.cancelando.set(false);
        this.proceso.set({
          id: p.id,
          estado: data.estado,
          progreso: data.progreso_estimado,
          error: null,
        });
      },
      error: (e: Error) => {
        this.cancelando.set(false);
        this.error.set(e.message);
      },
    });
  }

  reiniciar() {
    this.polling?.unsubscribe();
    this.cancelando.set(false);
    this.error.set('');
    this.proceso.set(null);
    this.file.set(null);
  }
}
