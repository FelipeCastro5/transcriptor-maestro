import { Routes } from '@angular/router';
import { SubirComponent } from './pages/subir.component';
import { MinutaComponent } from './pages/minuta.component';
import { HistorialComponent } from './pages/historial.component';
import { AcuerdosComponent } from './pages/acuerdos.component';
import { EquipoComponent } from './pages/equipo.component';
import { AuditoriaComponent } from './pages/auditoria.component';

export const routes: Routes = [
  { path: '', redirectTo: 'subir', pathMatch: 'full' },
  { path: 'subir', component: SubirComponent },
  { path: 'minuta/:id', component: MinutaComponent },
  { path: 'historial', component: HistorialComponent },
  { path: 'acuerdos', component: AcuerdosComponent },
  { path: 'equipo', component: EquipoComponent },
  { path: 'auditoria', component: AuditoriaComponent },
  { path: '**', redirectTo: 'subir' },
];
