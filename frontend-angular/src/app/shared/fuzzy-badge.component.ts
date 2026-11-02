import { Component, computed, input } from '@angular/core';

@Component({
  selector: 'app-fuzzy',
  template: `<span class="fuzzy" [class]="'fuzzy ' + nivel()">{{ pct() }}%</span>`,
})
export class FuzzyBadgeComponent {
  valor = input<number | null>(1);
  pct = computed(() => Math.round((this.valor() ?? 1) * 100));
  nivel = computed(() => (this.pct() >= 90 ? 'alta' : this.pct() >= 70 ? 'media' : 'baja'));
}
