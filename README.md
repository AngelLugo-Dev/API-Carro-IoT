# CarroIoT - Backend API

API REST con WebSocket para control remoto de carrito IoT. Desarrollado con Flask, arquitectura Modelo-Controlador y comunicación PUSH en tiempo real.

## 🚀 Características

- **Framework**: Flask 3.0 con Python 3.8+
- **Arquitectura**: Modelo-Controlador (OOP)
- **Base de Datos**: AWS Aurora RDS MySQL
- **WebSocket**: Flask-SocketIO para comunicación PUSH bidireccional
- **CORS**: Configurado para aceptar conexiones de cualquier IP
- **Puerto**: 5500
- **Escalabilidad**: Diseñado para múltiples dispositivos simultáneos

## 📁 Estructura del Proyecto

```
backend-api/
├── src/
│   ├── app.py                          # Aplicación principal Flask + SocketIO
│   ├── models/                         # Capa de Modelos (acceso a datos)
│   │   ├── __init__.py
│   │   ├── carrito.py                  # Modelo de dispositivos
│   │   └── movimiento.py               # Modelo de movimientos y eventos
│   ├── controllers/                    # Capa de Controladores (lógica de negocio)
│   │   ├── __init__.py
│   │   ├── carrito_controller.py       # Controlador de dispositivos
│   │   └── movimiento_controller.py    # Controlador de movimientos
│   ├── config/                         # Configuración
│   │   ├── __init__.py
│   │   └── database.py                 # Gestión de conexión a BD (Singleton)
│   └── utils/                          # Utilidades (futuro)
│       └── __init__.py
├── requirements.txt                    # Dependencias Python
├── .env.example                        # Template de variables de entorno
└── README.md                          # Este archivo
```

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
cd backend-api
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales de AWS Aurora RDS
```

Configurar las siguientes variables en `.env`:

```env
DB_HOST=your-aurora-cluster.cluster-xxxxxxxxxx.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your_password
DB_NAME=carrito_iot
SECRET_KEY=your-secret-key
```

### 5. Ejecutar la aplicación

```bash
cd src
python app.py
```

La API estará disponible en: `http://0.0.0.0:5500`

## 📡 API Endpoints

### Health Check

```http
GET /
GET /api/health
```

### Dispositivos (Carritos)

```http
GET    /api/devices              # Listar todos los dispositivos
GET    /api/devices/<id>         # Obtener dispositivo específico
POST   /api/devices/register     # Registrar nuevo dispositivo
```

**Ejemplo POST /api/devices/register:**

```json
{
  "device_name": "Carrito-001",
  "client_ip": "192.168.1.100",
  "country": "Mexico",
  "city": "CDMX",
  "latitude": 19.4326,
  "longitude": -99.1332
}
```

### Movimientos

```http
POST   /api/movements/send       # Enviar comando de movimiento
GET    /api/events/<device_id>   # Obtener historial de eventos
```

**Ejemplo POST /api/movements/send:**

```json
{
  "device_id": 1,
  "command": "forward",
  "duration_ms": 1000,
  "meta": {
    "speed": 100,
    "origin": "web_app"
  }
}
```

**Comandos disponibles:**

- `forward` - Adelante
- `backward` - Atrás
- `left` - Izquierda
- `right` - Derecha
- `stop` - Detener
- `rotate_left` - Giro 360° izquierda
- `rotate_right` - Giro 360° derecha
- `forward_left` - Adelante + Izquierda
- `forward_right` - Adelante + Derecha
- `backward_left` - Atrás + Izquierda
- `backward_right` - Atrás + Derecha

### Estados

```http
GET    /api/status/operational   # Obtener estados operacionales
```

## 🔌 WebSocket (PUSH Communication)

### Conexión

```javascript
const socket = io("http://localhost:5500");

socket.on("connect", () => {
  console.log("Conectado al servidor");
});
```

### Eventos del Cliente → Servidor

#### Registrar dispositivo

```javascript
socket.emit("register_device", {
  device_id: 1,
  device_name: "Carrito-001",
});
```

#### Enviar comando de movimiento

```javascript
socket.emit("movement_command", {
  device_id: 1,
  command: "forward",
  duration_ms: 1000,
  meta: {
    speed: 100,
    origin: "web_interface",
  },
});
```

#### Reportar obstáculo detectado

```javascript
socket.emit("obstacle_detected", {
  device_id: 1,
  status_clave: 1,
  meta: {
    distance_cm: 10,
    sensor: "ultrasonic",
  },
});
```

### Eventos del Servidor → Cliente

#### Ejecución de movimiento (PUSH al dispositivo)

```javascript
socket.on("execute_movement", (data) => {
  console.log("Ejecutar:", data.command);
  // { command: 'forward', duration_ms: 1000, timestamp: '...' }
});
```

#### Alerta de obstáculo

```javascript
socket.on("obstacle_alert", (data) => {
  console.log("Obstáculo detectado:", data);
});
```

#### Actualización de estado

```javascript
socket.on("status_update", (data) => {
  console.log("Estado del dispositivo:", data);
});
```

## 🗄️ Base de Datos

### Schema AWS Aurora RDS

El proyecto utiliza las siguientes tablas:

- **devices**: Dispositivos registrados
- **device_events**: Historial de eventos (movimientos, obstáculos)
- **op_status**: Estados operacionales (comandos de movimiento)
- **obstacle_status**: Estados de obstáculos
- **demos**: Demostraciones programadas (futuro)
- **demo_moves**: Movimientos de demostraciones (futuro)
- **scheduled_demo_runs**: Ejecuciones programadas (futuro)

Ver detalles completos en el schema proporcionado.

## 🔐 Seguridad

- **CORS**: Configurado para desarrollo (`origins: *`). En producción, especificar dominios permitidos.
- **Variables de entorno**: Credenciales sensibles en `.env` (no versionado)
- **AWS IAM**: Usar roles IAM en EC2 en lugar de credenciales hardcodeadas
- **HTTPS**: En producción, usar certificados SSL/TLS
- **Validación**: Todos los inputs son validados en los controladores

## 🚀 Despliegue en AWS EC2

### 1. Preparar EC2 Instance

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# Instalar nginx (opcional, para proxy reverso)
sudo apt install nginx -y
```

### 2. Clonar y configurar proyecto

```bash
git clone <your-repo-url>
cd backend-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar .env con credenciales Aurora RDS

### 4. Ejecutar con Gunicorn (producción)

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5500 src.app:app
```

### 5. Configurar como servicio systemd

```bash
sudo nano /etc/systemd/system/carrito-iot.service
```

```ini
[Unit]
Description=CarroIoT API Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend-api
Environment="PATH=/home/ubuntu/backend-api/venv/bin"
ExecStart=/home/ubuntu/backend-api/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5500 src.app:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start carrito-iot
sudo systemctl enable carrito-iot
```

## 📊 Monitoring

Ver logs en tiempo real:

```bash
sudo journalctl -u carrito-iot -f
```

## 🧪 Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-flask

# Ejecutar tests (cuando estén disponibles)
pytest
```

## 📝 Notas de Desarrollo

- **Patrón Singleton**: La clase `Database` implementa Singleton para reutilizar conexiones
- **Context Managers**: Uso de `with` para gestión automática de cursores y transacciones
- **OOP**: Separación clara entre Modelos (datos) y Controladores (lógica)
- **Escalabilidad**: Diseñado para soportar múltiples dispositivos mediante rooms de WebSocket
- **Logging**: Logs detallados en consola para debugging

## 🔮 Futuras Mejoras

- [ ] Autenticación JWT para endpoints
- [ ] Rate limiting para prevenir abuso
- [ ] Sistema de demos programados (ya está en DB schema)
- [ ] Dashboard de monitoreo en tiempo real
- [ ] Métricas con Prometheus/Grafana
- [ ] Tests unitarios y de integración
- [ ] CI/CD pipeline
- [ ] Docker containerization

## 👨‍💻 Autor

Desarrollado para el proyecto CarroIoT
Fecha: 2025

## 📄 Licencia

Proyecto privado - Todos los derechos reservados
