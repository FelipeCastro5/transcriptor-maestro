// Configuración de entorno de desarrollo local.
// apiUrl vacío ('') delega al proxy local de Angular (proxy.conf.json -> http://127.0.0.1:8000).
// Si deseas consumir directamente el backend sin pasar por el proxy, puedes definir 'http://localhost:8000'.
export const environment = {
  production: false,
  apiUrl: '',
};
