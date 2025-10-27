"""
Controlador: Movimiento
Gestiona la lógica de negocio para movimientos y eventos del carrito
Maneja WebSocket PUSH notifications y logging de eventos
"""

from models.movimiento import Movimiento
from datetime import datetime


class MovimientoController:
    """
    Controlador para gestionar operaciones de movimiento y eventos
    Integra WebSocket para comunicación en tiempo real
    """
    
    def __init__(self, db, socketio=None):
        """
        Inicializa el controlador con la conexión a base de datos y SocketIO
        
        Args:
            db (Database): Instancia de la clase Database
            socketio (SocketIO, optional): Instancia de SocketIO para PUSH
        """
        self.movimiento_model = Movimiento(db)
        self.socketio = socketio
        print('[MovimientoController] Controlador inicializado')
    
    def send_movement_command(self, command_data):
        """
        Procesa y envía un comando de movimiento al dispositivo
        
        Args:
            command_data (dict): Datos del comando
                - device_id (int): ID del dispositivo
                - command (str): Comando de movimiento
                - duration_ms (int, optional): Duración en milisegundos
                - meta (dict, optional): Metadatos adicionales
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar datos requeridos
            device_id = command_data.get('device_id')
            command = command_data.get('command')
            
            if not device_id:
                return {
                    'success': False,
                    'error': 'device_id es requerido'
                }
            
            if not command:
                return {
                    'success': False,
                    'error': 'command es requerido'
                }
            
            # Validar que el comando sea válido
            if not self.movimiento_model.validate_command(command):
                return {
                    'success': False,
                    'error': f'Comando inválido: {command}',
                    'valid_commands': list(self.movimiento_model.MOVEMENT_COMMANDS.keys())
                }
            
            # Preparar metadatos
            meta = command_data.get('meta', {})
            meta['duration_ms'] = command_data.get('duration_ms', 1000)
            meta['timestamp'] = datetime.now().isoformat()
            meta['source'] = 'api_rest'
            
            # Registrar evento en base de datos
            event_id = self.movimiento_model.log_movement_event(
                device_id=device_id,
                command=command,
                meta=meta
            )
            
            # Enviar comando via WebSocket si está disponible
            if self.socketio:
                room = f'device_{device_id}'
                self.socketio.emit('execute_movement', {
                    'command': command,
                    'duration_ms': meta['duration_ms'],
                    'timestamp': meta['timestamp'],
                    'event_id': event_id
                }, room=room)
                
                print(f'[MovimientoController] Comando WebSocket enviado a {room}: {command}')
            
            return {
                'success': True,
                'message': f'Comando {command} enviado exitosamente',
                'event_id': event_id,
                'device_id': device_id,
                'command': command
            }
            
        except Exception as e:
            print(f'[MovimientoController] Error al enviar comando: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_websocket_command(self, command_data):
        """
        Procesa un comando recibido por WebSocket
        Similar a send_movement_command pero optimizado para WebSocket
        
        Args:
            command_data (dict): Datos del comando desde WebSocket
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            device_id = command_data.get('device_id')
            command = command_data.get('command')
            
            if not device_id or not command:
                return {
                    'success': False,
                    'error': 'device_id y command son requeridos'
                }
            
            # Validar comando
            if not self.movimiento_model.validate_command(command):
                return {
                    'success': False,
                    'error': f'Comando inválido: {command}'
                }
            
            # Preparar metadatos
            meta = command_data.get('meta', {})
            meta['duration_ms'] = command_data.get('duration_ms', 1000)
            meta['timestamp'] = datetime.now().isoformat()
            meta['source'] = 'websocket'
            
            # Registrar evento
            event_id = self.movimiento_model.log_movement_event(
                device_id=device_id,
                command=command,
                meta=meta
            )
            
            print(f'[MovimientoController] Comando WebSocket procesado: {command} para dispositivo {device_id}')
            
            return {
                'success': True,
                'message': 'Comando procesado exitosamente',
                'event_id': event_id,
                'device_id': device_id,
                'command': command
            }
            
        except Exception as e:
            print(f'[MovimientoController] Error al procesar comando WebSocket: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_obstacle_event(self, obstacle_data):
        """
        Registra un evento de detección de obstáculo
        
        Args:
            obstacle_data (dict): Datos del obstáculo
                - device_id (int): ID del dispositivo
                - status_clave (int): Código del estado de obstáculo
                - meta (dict, optional): Metadatos (distancia, sensor, etc.)
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            device_id = obstacle_data.get('device_id')
            status_clave = obstacle_data.get('status_clave')
            
            if not device_id:
                return {
                    'success': False,
                    'error': 'device_id es requerido'
                }
            
            if status_clave is None:
                return {
                    'success': False,
                    'error': 'status_clave es requerido'
                }
            
            # Preparar metadatos
            meta = obstacle_data.get('meta', {})
            meta['timestamp'] = datetime.now().isoformat()
            
            # Registrar evento
            event_id = self.movimiento_model.log_obstacle_event(
                device_id=device_id,
                status_clave=status_clave,
                meta=meta
            )
            
            # Enviar alerta via WebSocket
            if self.socketio:
                self.socketio.emit('obstacle_alert', {
                    'device_id': device_id,
                    'status_clave': status_clave,
                    'timestamp': meta['timestamp'],
                    'event_id': event_id,
                    'meta': meta
                }, broadcast=True)
                
                print(f'[MovimientoController] Alerta de obstáculo enviada para dispositivo {device_id}')
            
            return {
                'success': True,
                'message': 'Evento de obstáculo registrado',
                'event_id': event_id,
                'device_id': device_id
            }
            
        except Exception as e:
            print(f'[MovimientoController] Error al registrar obstáculo: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_device_events(self, device_id, limit=50, event_type=None):
        """
        Obtiene el historial de eventos de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            limit (int): Número máximo de eventos
            event_type (str, optional): Filtrar por tipo de evento
        
        Returns:
            list: Lista de eventos serializados
        """
        try:
            events = self.movimiento_model.get_device_events(
                device_id=device_id,
                limit=limit,
                event_type=event_type
            )
            
            # Serializar eventos
            serialized_events = [self._serialize_event(event) for event in events]
            
            print(f'[MovimientoController] {len(serialized_events)} eventos obtenidos para dispositivo {device_id}')
            return serialized_events
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener eventos: {str(e)}')
            raise
    
    def get_all_op_status(self):
        """
        Obtiene todos los estados operacionales disponibles
        
        Returns:
            list: Lista de estados operacionales
        """
        try:
            statuses = self.movimiento_model.get_all_op_status()
            print(f'[MovimientoController] {len(statuses)} estados operacionales obtenidos')
            return statuses
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener estados: {str(e)}')
            raise
    
    def get_all_obstacle_status(self):
        """
        Obtiene todos los estados de obstáculos disponibles
        
        Returns:
            list: Lista de estados de obstáculos
        """
        try:
            statuses = self.movimiento_model.get_all_obstacle_status()
            print(f'[MovimientoController] {len(statuses)} estados de obstáculos obtenidos')
            return statuses
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener estados de obstáculos: {str(e)}')
            raise
    
    def get_last_movement(self, device_id):
        """
        Obtiene el último movimiento de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            dict: Último movimiento o None
        """
        try:
            movement = self.movimiento_model.get_last_movement(device_id)
            
            if movement:
                movement = self._serialize_event(movement)
                print(f'[MovimientoController] Último movimiento obtenido para dispositivo {device_id}')
            else:
                print(f'[MovimientoController] No hay movimientos para dispositivo {device_id}')
            
            return movement
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener último movimiento: {str(e)}')
            raise
    
    def get_recent_obstacles(self, device_id, minutes=30):
        """
        Obtiene obstáculos recientes de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            minutes (int): Ventana de tiempo en minutos
        
        Returns:
            list: Lista de obstáculos recientes
        """
        try:
            obstacles = self.movimiento_model.get_recent_obstacles(
                device_id=device_id,
                minutes=minutes
            )
            
            serialized_obstacles = [self._serialize_event(obs) for obs in obstacles]
            
            print(f'[MovimientoController] {len(serialized_obstacles)} obstáculos recientes para dispositivo {device_id}')
            return serialized_obstacles
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener obstáculos recientes: {str(e)}')
            raise
    
    def get_movement_statistics(self, device_id, days=7):
        """
        Obtiene estadísticas de movimiento
        
        Args:
            device_id (int): ID del dispositivo
            days (int): Número de días hacia atrás
        
        Returns:
            dict: Estadísticas de movimiento
        """
        try:
            stats = self.movimiento_model.get_movement_statistics(
                device_id=device_id,
                days=days
            )
            
            # Serializar fechas
            for stat in stats:
                if isinstance(stat.get('first_occurrence'), datetime):
                    stat['first_occurrence'] = stat['first_occurrence'].isoformat()
                if isinstance(stat.get('last_occurrence'), datetime):
                    stat['last_occurrence'] = stat['last_occurrence'].isoformat()
            
            print(f'[MovimientoController] Estadísticas obtenidas para dispositivo {device_id}')
            return stats
            
        except Exception as e:
            print(f'[MovimientoController] Error al obtener estadísticas: {str(e)}')
            raise
    
    def broadcast_status_update(self, device_id, status_data):
        """
        Broadcast de actualización de estado a todos los clientes conectados
        
        Args:
            device_id (int): ID del dispositivo
            status_data (dict): Datos de estado a transmitir
        """
        if self.socketio:
            self.socketio.emit('status_update', {
                'device_id': device_id,
                'status': status_data,
                'timestamp': datetime.now().isoformat()
            }, broadcast=True)
            
            print(f'[MovimientoController] Estado actualizado broadcast para dispositivo {device_id}')
    
    def get_available_commands(self):
        """
        Obtiene la lista de comandos disponibles
        
        Returns:
            dict: Diccionario con comandos y sus códigos
        """
        return self.movimiento_model.MOVEMENT_COMMANDS.copy()
    
    def _serialize_event(self, event):
        """
        Serializa un evento convirtiendo datetime a string
        
        Args:
            event (dict): Evento a serializar
        
        Returns:
            dict: Evento serializado
        """
        if not event:
            return None
        
        serialized = event.copy()
        
        # Convertir datetime a ISO format string
        if isinstance(serialized.get('event_ts'), datetime):
            serialized['event_ts'] = serialized['event_ts'].isoformat()
        
        if isinstance(serialized.get('first_occurrence'), datetime):
            serialized['first_occurrence'] = serialized['first_occurrence'].isoformat()
        
        if isinstance(serialized.get('last_occurrence'), datetime):
            serialized['last_occurrence'] = serialized['last_occurrence'].isoformat()
        
        return serialized
