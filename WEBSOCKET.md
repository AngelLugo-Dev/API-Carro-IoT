# Conexión WebSocket (Socket.IO)

## URL de Conexión WebSocket

**IMPORTANTE:** La conexión WebSocket usa la **misma URL HTTP** que la API REST. No necesitas una URL diferente.

### URLs de Conexión

```
HTTP (Desarrollo local):
- API REST: http://localhost:5500
- WebSocket: http://localhost:5500  ← MISMA URL

HTTP (Servidor de producción):
- API REST: http://TU_IP_PUBLICA:5500
- WebSocket: http://TU_IP_PUBLICA:5500  ← MISMA URL

HTTPS (Con certificado SSL):
- API REST: https://TU_DOMINIO:5500
- WebSocket: https://TU_DOMINIO:5500  ← MISMA URL
```

## ¿Por qué la misma URL?

Este servidor usa **Socket.IO**, que automáticamente:
1. Se conecta inicialmente por HTTP/HTTPS
2. Negocia la actualización a WebSocket si está disponible
3. Usa polling HTTP como respaldo si WebSocket falla

Socket.IO maneja toda esta lógica internamente en la ruta `/socket.io`.

## Configuración del Cliente

### JavaScript (Socket.IO Client)

```javascript
// config.js
const config = {
    // Usa la misma URL para ambos
    API_BASE_URL: "http://TU_IP_PUBLICA:5500",
    WEBSOCKET_URL: "http://TU_IP_PUBLICA:5500"  // Misma URL
};

// Conexión
const socket = io(config.WEBSOCKET_URL, {
    transports: ['websocket', 'polling'],  // WebSocket primero, polling como respaldo
    path: '/socket.io',  // Ruta por defecto (opcional)
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5
});
```

### Python (Socket.IO Client)

```python
import socketio

sio = socketio.Client()

# Misma URL HTTP
sio.connect('http://TU_IP_PUBLICA:5500')
```

### Arduino/ESP32

```cpp
#include <SocketIOclient.h>

SocketIOclient socketIO;

void setup() {
    // Misma URL HTTP (sin protocolo ws://)
    socketIO.begin("TU_IP_PUBLICA", 5500, "/socket.io/");
}
```

## Eventos Disponibles

### Cliente → Servidor

```javascript
// Registrar dispositivo
socket.emit('register_device', {
    device_id: 1,
    device_name: 'Arduino-ESP32-01'
});

// Enviar comando de movimiento
socket.emit('movement_command', {
    device_id: 1,
    command: 'forward',
    duration_ms: 1000
});

// Ping
socket.emit('ping');
```

### Servidor → Cliente

```javascript
// Respuesta de conexión
socket.on('connection_response', (data) => {
    console.log(data.message); // "Conectado al servidor"
});

// Registro exitoso
socket.on('registration_success', (data) => {
    console.log(`Device ${data.device_id} registrado`);
});

// Comando recibido
socket.on('execute_movement', (data) => {
    console.log(`Ejecutar: ${data.command} por ${data.duration_ms}ms`);
});

// Pong
socket.on('pong', (data) => {
    console.log('Pong recibido');
});
```

## Solución de Problemas

### "WebSocket connection failed" o "Connection rejected"

**Causas comunes:**

1. **CORS no configurado correctamente**
   - Verifica que tu dominio esté en `cors_allow_origins` en `.env`
   - Para desarrollo, puedes usar `"*"` (no recomendado en producción)

2. **Puerto bloqueado por firewall**
   - En AWS EC2: Abre el puerto 5500 en el Security Group
   - En Windows Server: Agrega regla de entrada para TCP 5500
   - En Linux: `sudo ufw allow 5500`

3. **Servidor no está corriendo**
   - Verifica que uvicorn esté ejecutándose en el puerto 5500
   - Comando: `netstat -an | grep 5500` (Linux/Mac)
   - PowerShell: `Get-NetTCPConnection -LocalPort 5500`

4. **Intentando usar protocolo ws:// o wss://**
   - ❌ INCORRECTO: `ws://TU_IP:5500`
   - ❌ INCORRECTO: `wss://TU_IP:5500`
   - ✅ CORRECTO: `http://TU_IP:5500`
   - ✅ CORRECTO: `https://TU_IP:5500`

5. **Path incorrecto**
   - Socket.IO usa `/socket.io` por defecto
   - No uses paths como `/ws` o `/websocket`

### Verificar la Conexión

#### Desde el navegador (JavaScript Console):

```javascript
const socket = io('http://TU_IP_PUBLICA:5500', {
    transports: ['websocket', 'polling']
});

socket.on('connect', () => {
    console.log('✅ Conectado! ID:', socket.id);
});

socket.on('connect_error', (error) => {
    console.error('❌ Error de conexión:', error.message);
});

socket.on('connection_response', (data) => {
    console.log('📡 Respuesta del servidor:', data);
});
```

#### Desde curl (verificar que el servidor está corriendo):

```bash
# Verificar endpoint HTTP
curl http://TU_IP_PUBLICA:5500/api/health

# Socket.IO handshake (debe retornar JSON)
curl "http://TU_IP_PUBLICA:5500/socket.io/?EIO=4&transport=polling"
```

### Logs del Servidor

Para ver logs de conexiones WebSocket, ejecuta el servidor con logs habilitados:

```python
# En app/services/websocket_manager.py, cambia:
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_allow_origins,
    logger=True,        # Cambiar a True
    engineio_logger=True,  # Cambiar a True
    ping_interval=25,
    ping_timeout=60,
)
```

## Ejemplo Completo: Cliente Web

```html
<!DOCTYPE html>
<html>
<head>
    <title>IoT Car Control - WebSocket Test</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status">Desconectado</div>
    <button onclick="connectWS()">Conectar</button>
    <button onclick="registerDevice()">Registrar Dispositivo</button>
    
    <script>
        let socket;
        
        function connectWS() {
            // IMPORTANTE: Usa la misma URL HTTP, no ws://
            socket = io('http://TU_IP_PUBLICA:5500', {
                transports: ['websocket', 'polling']
            });
            
            socket.on('connect', () => {
                document.getElementById('status').innerText = 
                    '✅ Conectado - ID: ' + socket.id;
            });
            
            socket.on('disconnect', () => {
                document.getElementById('status').innerText = '❌ Desconectado';
            });
            
            socket.on('connection_response', (data) => {
                console.log('Servidor dice:', data.message);
            });
            
            socket.on('registration_success', (data) => {
                console.log('Dispositivo registrado:', data);
            });
        }
        
        function registerDevice() {
            if (!socket || !socket.connected) {
                alert('Primero conecta el WebSocket');
                return;
            }
            
            socket.emit('register_device', {
                device_id: 1,
                device_name: 'Test-Device'
            });
        }
    </script>
</body>
</html>
```

## Resumen

- ✅ Usa la **misma URL HTTP/HTTPS** para WebSocket y REST API
- ✅ Socket.IO maneja el upgrade a WebSocket automáticamente
- ✅ No necesitas protocolo `ws://` o `wss://`
- ✅ La ruta por defecto es `/socket.io` (manejada automáticamente)
- ✅ Verifica CORS y firewall si tienes problemas de conexión

Para más información sobre eventos Socket.IO disponibles, consulta el archivo `README.md`.
