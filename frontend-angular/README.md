# 🅰️ Transcriptor Maestro - Frontend Angular

Interfaz web en **Angular 19** (componentes standalone + signals) que consume el backend FastAPI según [`backend/FRONTEND_HANDOFF.md`](../backend/FRONTEND_HANDOFF.md).

## Cómo ejecutarlo

Requisitos: **Node.js 18+** y el backend encendido en `http://127.0.0.1:8000`.

```powershell
cd frontend-angular
npm start
```

`npm start` ejecuta primero `npm install` automáticamente (script `prestart`), así que no hace falta instalar dependencias a mano.

Abre 👉 [http://localhost:4200](http://localhost:4200)

`npm start` ejecuta `ng serve`, que redirige `/api` y `/health` al backend mediante [`proxy.conf.json`](./proxy.conf.json). No hace falta configurar CORS.
Si el backend está en otro servidor, cambia `apiUrl` en [`src/environments/environment.ts`](./src/environments/environment.ts).

Compilar para producción: `npx ng build` (genera `dist/frontend-angular/`).

## Estructura

```text
src/app/
├── app.component.ts        # Barra superior, pestañas e indicador "API en línea"
├── app.routes.ts           # Rutas: /subir, /minuta/:id, /historial, /acuerdos, /equipo, /auditoria
├── core/
│   ├── api.service.ts      # Todas las llamadas HTTP (ResponseDto<T>)
│   └── models.ts           # Interfaces TypeScript de los contratos del backend
├── shared/
│   ├── tabla-acuerdos.component.ts   # Tabla de acuerdos con cambio de estado y cita textual
│   └── fuzzy-badge.component.ts      # Indicador % de coincidencia Fuzzy
└── pages/
    ├── subir.component.ts      # Drag & drop, configuración IA y polling cada 2.5 s
    ├── minuta.component.ts     # Resumen, acuerdos y transcripción
    ├── historial.component.ts  # Listado de reuniones
    ├── acuerdos.component.ts   # Kanban pendiente / completado / atrasado
    ├── equipo.component.ts     # Catálogo de responsables y alta de integrantes
    └── auditoria.component.ts  # Métricas IA, simulación VACAS, logs y caché
```

## Prueba rápida sin API keys

Sube un `.txt` con:

```
Juancho debe entregar el informe de ventas el viernes. Carlitos acordó revisar la base de datos mañana.
```

y elige la **Estrategia 1 (Reglas offline)**: “Juancho” se asigna a *Juan Pérez* y “Carlitos” a *Carlos Ruiz*.
