"""
API Backend para Control de Carrito IoT
Autor: Desarrollado para CarroIoT
Descripción: API principal con Flask y WebSocket para control remoto de carrito IoT
Puerto: 5500
Arquitectura: Modelo-Controlador con OOP
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from datetime import datetime
from dotenv import load_dotenv

# Importar controladores
from controllers.carrito_controller import CarritoController
from controllers.movimiento_controller import MovimientoController

# Importar configuración de base de datos
from config.database import Database

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'carrito-iot-secret-key-2025')

# Configurar CORS para aceptar cualquier IP
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializar SocketIO con configuración PUSH
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)

# Inicializar base de datos
db = Database()

# Inicializar controladores
carrito_controller = CarritoController(db)
movimiento_controller = MovimientoController(db, socketio)

# =====================================================
# RUTAS HTTP REST API
# =====================================================

@app.route('/', methods=['GET'])
def home():
    """
    Ruta principal - Health check
    """
    return jsonify({
        'status': 'online',
        'service': 'CarroIoT API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'websocket': 'enabled',
        'port': 5500
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Verifica el estado de la API y la conexión a la base de datos
    """
    db_status = db.check_connection()
    return jsonify({
        'api': 'healthy',
        'database': 'connected' if db_status else 'disconnected',
        'timestamp': datetime.now().isoformat()
    }), 200 if db_status else 503


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """
    Obtiene la lista de todos los dispositivos registrados
    """
    try:
        devices = carrito_controller.get_all_devices()
        return jsonify({
            'success': True,
            'count': len(devices),
            'devices': devices
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """
    Obtiene información de un dispositivo específico
    """
    try:
        device = carrito_controller.get_device_by_id(device_id)
        if device:
            return jsonify({
                'success': True,
                'device': device
            }), 200
        return jsonify({
            'success': False,
            'error': 'Device not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/devices/register', methods=['POST'])
def register_device():
    """
    Registra un nuevo dispositivo en el sistema
    Body: {
        "device_name": "Carrito-001",
        "client_ip": "192.168.1.100",
        "country": "Mexico",
        "city": "CDMX",
        "latitude": 19.4326,
        "longitude": -99.1332
    }
    """
    try:
        data = request.get_json()
        device_id = carrito_controller.register_device(data)
        return jsonify({
            'success': True,
            'message': 'Device registered successfully',
            'device_id': device_id
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/movements/send', methods=['POST'])
def send_movement():
    """
    Envía un comando de movimiento al carrito vía WebSocket
    Body: {
        "device_id": 1,
        "command": "forward",
        "duration_ms": 1000,
        "meta": {"speed": 100}
    }
    """
    try:
        data = request.get_json()
        result = movimiento_controller.send_movement_command(data)
        return jsonify(result), 200 if result['success'] else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/events/<int:device_id>', methods=['GET'])
def get_device_events(device_id):
    """
    Obtiene el historial de eventos de un dispositivo
    Query params: limit (default: 50)
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        events = movimiento_controller.get_device_events(device_id, limit)
        return jsonify({
            'success': True,
            'device_id': device_id,
            'count': len(events),
            'events': events
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/status/operational', methods=['GET'])
def get_operational_status():
    """
    Obtiene todos los estados operacionales disponibles
    """
    try:
        statuses = movimiento_controller.get_all_op_status()
        return jsonify({
            'success': True,
            'count': len(statuses),
            'statuses': statuses
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================
# WEBSOCKET EVENTOS
# =====================================================

@socketio.on('connect')
def handle_connect():
    """
    Maneja la conexión de un nuevo cliente WebSocket
    """
    client_ip = request.remote_addr
    print(f'[WebSocket] Cliente conectado: {client_ip} - SID: {request.sid}')
    emit('connection_response', {
        'status': 'connected',
        'message': 'Conectado exitosamente al servidor CarroIoT',
        'timestamp': datetime.now().isoformat(),
        'sid': request.sid
    })


@socketio.on('disconnect')
def handle_disconnect():
    """
    Maneja la desconexión de un cliente WebSocket
    """
    print(f'[WebSocket] Cliente desconectado: {request.sid}')


@socketio.on('register_device')
def handle_register_device(data):
    """
    Registra un dispositivo y lo une a su sala específica
    Data: {
        "device_id": 1,
        "device_name": "Carrito-001"
    }
    """
    try:
        device_id = data.get('device_id')
        room = f'device_{device_id}'
        join_room(room)
        
        print(f'[WebSocket] Dispositivo {device_id} unido a sala {room}')
        
        emit('registration_success', {
            'success': True,
            'device_id': device_id,
            'room': room,
            'message': f'Dispositivo registrado en sala {room}',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        emit('registration_error', {
            'success': False,
            'error': str(e)
        })


@socketio.on('unregister_device')
def handle_unregister_device(data):
    """
    Desregistra un dispositivo de su sala
    """
    try:
        device_id = data.get('device_id')
        room = f'device_{device_id}'
        leave_room(room)
        
        print(f'[WebSocket] Dispositivo {device_id} salió de sala {room}')
        
        emit('unregistration_success', {
            'success': True,
            'device_id': device_id,
            'message': 'Dispositivo desregistrado exitosamente'
        })
    except Exception as e:
        emit('unregistration_error', {
            'success': False,
            'error': str(e)
        })


@socketio.on('movement_command')
def handle_movement_command(data):
    """
    Recibe y procesa comandos de movimiento en tiempo real
    Data: {
        "device_id": 1,
        "command": "forward|backward|left|right|stop|rotate_left|rotate_right",
        "duration_ms": 1000,
        "meta": {"speed": 100, "origin": "web_app"}
    }
    """
    try:
        result = movimiento_controller.process_websocket_command(data)
        
        if result['success']:
            # Enviar comando al dispositivo específico via PUSH
            room = f"device_{data['device_id']}"
            socketio.emit('execute_movement', {
                'command': data['command'],
                'duration_ms': data.get('duration_ms', 1000),
                'timestamp': datetime.now().isoformat(),
                'meta': data.get('meta', {})
            }, room=room)
            
            # Confirmar al cliente que envió el comando
            emit('command_sent', result)
            
            print(f"[WebSocket] Comando enviado a dispositivo {data['device_id']}: {data['command']}")
        else:
            emit('command_error', result)
            
    except Exception as e:
        emit('command_error', {
            'success': False,
            'error': str(e)
        })


@socketio.on('obstacle_detected')
def handle_obstacle_detected(data):
    """
    Recibe notificación de obstáculo detectado por el carrito
    Data: {
        "device_id": 1,
        "status_clave": 1,
        "meta": {"distance_cm": 10, "sensor": "ultrasonic"}
    }
    """
    try:
        result = movimiento_controller.log_obstacle_event(data)
        
        # Notificar a todos los clientes conectados
        socketio.emit('obstacle_alert', {
            'device_id': data['device_id'],
            'status': data.get('status_clave'),
            'timestamp': datetime.now().isoformat(),
            'meta': data.get('meta', {})
        }, broadcast=True)
        
        emit('obstacle_logged', result)
        
    except Exception as e:
        emit('error', {
            'success': False,
            'error': str(e)
        })


@socketio.on('device_status')
def handle_device_status(data):
    """
    Recibe y transmite el estado actual del dispositivo
    Data: {
        "device_id": 1,
        "battery": 85,
        "signal_strength": 90,
        "online": true
    }
    """
    try:
        # Broadcast el estado a todos los clientes interesados
        socketio.emit('status_update', {
            'device_id': data['device_id'],
            'status': data,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)
        
    except Exception as e:
        print(f'[WebSocket] Error en device_status: {str(e)}')


@socketio.on('ping')
def handle_ping():
    """
    Maneja ping para mantener conexión activa
    """
    emit('pong', {
        'timestamp': datetime.now().isoformat()
    })


# =====================================================
# MANEJO DE ERRORES
# =====================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'code': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'code': 500
    }), 500


# =====================================================
# PUNTO DE ENTRADA
# =====================================================

if __name__ == '__main__':
    print('=' * 60)
    print('🚗 CarroIoT API Server')
    print('=' * 60)
    print(f'Puerto: 5500')
    print(f'CORS: Habilitado para todas las IPs')
    print(f'WebSocket: Habilitado (PUSH notifications)')
    print(f'Timestamp: {datetime.now().isoformat()}')
    print('=' * 60)
    
    # Iniciar servidor con SocketIO
    socketio.run(
        app,
        host='0.0.0.0',  # Acepta conexiones de cualquier IP
        port=5500,
        debug=True,
        allow_unsafe_werkzeug=True
    )
