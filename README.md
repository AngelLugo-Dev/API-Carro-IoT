# Backend IoT Car Control (FastAPI + Socket.IO)

API en arquitectura MVC con comunicaciones push por Socket.IO, compatible con el frontend publicado en GitHub Pages.

- Framework: FastAPI (REST) + python-socketio (ASGI)
- WebSocket: Socket.IO (eventos: register_device, movement_command, etc.)
- Puerto: 5500
- CORS: abierto y con whitelist al dominio de GitHub Pages
- Base de datos: MySQL en AWS RDS (usa SPs ya creados)

## 📖 Documentación

- **[WEBSOCKET.md](./WEBSOCKET.md)** - Guía completa de conexión WebSocket (URLs, configuración, solución de problemas)

## Estructura

```
backend/
  requirements.txt
  app/
    main.py                 # Punto de entrada ASGI (REST + Socket.IO)
    config.py               # Variables de entorno y settings
    db.py                   # Conexión MySQL y helpers
    models/
      commands_map.py       # Mapeo comando -> status_clave
    repositories/
      device_repository.py  # Acceso a devices
      events_repository.py  # Acceso a eventos/estatus
      demo_repository.py    # Acceso a demos (SP)
    services/
      websocket_manager.py  # Servidor Socket.IO y helpers
    controllers/
      socket_handlers.py    # Manejadores de eventos Socket.IO
    routers/
      health.py             # GET /api/health
      devices.py            # /api/devices
      movements.py          # /api/movements
      events.py             # /api/events
      status.py             # /api/status
      simulate.py           # /api/simulate
```

## Configuración (Windows Server EC2)

1. Instalar Python 3.11 (x64) y agregar a PATH.
2. Clonar el repo en el servidor.
3. Crear y activar un entorno virtual (recomendado).

```powershell
# En la carpeta backend/
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Crear archivo `.env` con credenciales de RDS (usa los mismos nombres del ejemplo):

```
# backend/.env (ejemplo)
app_name="IoT Car Control API"
environment="production"
host="0.0.0.0"
port="5500"
cors_allow_origins="https://angellugo-dev.github.io,https://angellugo-dev.github.io/frontend-web-iot"

# MySQL RDS
db_host="instance-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com"
db_port="3306"
db_user="admin"
db_password="REEMPLAZA_POR_TU_PASSWORD"
db_name="iot_car_control"
```

Notas:

- También puedes exportar las variables como estándar: DB_HOST, DB_USER, etc. El archivo `.env` es lo más sencillo.
- No subas las credenciales al repositorio.

5. Ejecutar el servidor (puerto 5500):

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 5500 --workers 1
```

Sugerencia: crea una regla de seguridad en el Security Group de tu instancia que permita el puerto 5500 desde tu IP o 0.0.0.0/0 si es demo.

## Endpoints REST principales

- GET /api/health
- GET /api/devices
- GET /api/devices/{id}
- POST /api/devices/register
- POST /api/movements/send
- POST /api/movements/sequence
- GET /api/events/{deviceId}?limit=50
- GET /api/status/operational
- POST /api/simulate/obstacle

## Eventos Socket.IO

Cliente emite:

- `register_device` { device_id, device_name }
- `unregister_device` { device_id }
- `movement_command` { device_id, command, duration_ms, meta? }
- `ping`

Servidor emite:

- `connection_response` { status, message }
- `registration_success` { device_id, device_name }
- `registration_error` { error }
- `command_sent` { device_id, command, status_clave, duration_ms, meta }
- `command_error` { error }
- `execute_movement` { ... } (cuando llega via REST)
- `obstacle_alert` { device_id, status_clave, meta }
- `status_update` { ... }

## Conexión Frontend (GitHub Pages)

En `frontend-web/js/config.js`, establece:

```js
API_BASE_URL: "http://TU_IP_PUBLICA:5500",
WEBSOCKET_URL: "http://TU_IP_PUBLICA:5500",  // Misma URL que la API
```

**IMPORTANTE:** WebSocket usa la misma URL HTTP que la API REST. Socket.IO maneja automáticamente el upgrade a WebSocket.

📖 **Para más detalles sobre conexiones WebSocket, consulta [WEBSOCKET.md](./WEBSOCKET.md)**

## Notas de despliegue

- Windows Server no necesita Nginx para esta demo; puedes ejecutar uvicorn como servicio con NSSM o un Programador de tareas.
- Abre el puerto en el firewall de Windows: Inbound rule para TCP 5500.
- Si luego quieres HTTPS, coloca un reverse proxy (Nginx/IIS) al frente.
