"""
Modelo: Movimiento (Device Events & Status)
Gestiona los eventos de movimiento, obstáculos y estados operacionales
Mapea las tablas: device_events, op_status, obstacle_status
"""

from datetime import datetime
import json


class Movimiento:
    """
    Clase que representa los movimientos y eventos del carrito
    Gestiona estados operacionales y detección de obstáculos
    """
    
    # Definición de comandos de movimiento disponibles
    MOVEMENT_COMMANDS = {
        'forward': 1,           # Adelante
        'backward': 2,          # Atrás
        'left': 3,              # Izquierda
        'right': 4,             # Derecha
        'stop': 5,              # Detener
        'rotate_left': 6,       # Giro 360° izquierda
        'rotate_right': 7,      # Giro 360° derecha
        'forward_left': 8,      # Adelante + Izquierda
        'forward_right': 9,     # Adelante + Derecha
        'backward_left': 10,    # Atrás + Izquierda
        'backward_right': 11    # Atrás + Derecha
    }
    
    def __init__(self, db):
        """
        Inicializa el modelo con la conexión a base de datos
        
        Args:
            db (Database): Instancia de la clase Database
        """
        self.db = db
        self.events_table = 'device_events'
        self.op_status_table = 'op_status'
        self.obstacle_status_table = 'obstacle_status'
    
    def log_movement_event(self, device_id, command, meta=None, demo_id=None):
        """
        Registra un evento de movimiento en la base de datos
        
        Args:
            device_id (int): ID del dispositivo
            command (str): Comando de movimiento
            meta (dict, optional): Metadatos adicionales (velocidad, duración, etc.)
            demo_id (int, optional): ID del demo si aplica
        
        Returns:
            int: ID del evento creado
        """
        status_clave = self.MOVEMENT_COMMANDS.get(command, 5)  # Default: stop
        
        query = """
        INSERT INTO device_events (
            device_id,
            event_type,
            status_clave,
            demo_id,
            event_ts,
            meta
        ) VALUES (
            %(device_id)s,
            'movement',
            %(status_clave)s,
            %(demo_id)s,
            NOW(),
            %(meta)s
        )
        """
        
        params = {
            'device_id': device_id,
            'status_clave': status_clave,
            'demo_id': demo_id,
            'meta': json.dumps(meta) if meta else None
        }
        
        event_id = self.db.execute_insert(query, params)
        print(f'[Movimiento Model] Evento de movimiento registrado: ID {event_id}, Comando: {command}')
        return event_id
    
    def log_obstacle_event(self, device_id, status_clave, meta=None):
        """
        Registra un evento de detección de obstáculo
        
        Args:
            device_id (int): ID del dispositivo
            status_clave (int): Clave del estado de obstáculo
            meta (dict, optional): Metadatos (distancia, sensor, etc.)
        
        Returns:
            int: ID del evento creado
        """
        query = """
        INSERT INTO device_events (
            device_id,
            event_type,
            status_clave,
            event_ts,
            meta
        ) VALUES (
            %(device_id)s,
            'obstacle',
            %(status_clave)s,
            NOW(),
            %(meta)s
        )
        """
        
        params = {
            'device_id': device_id,
            'status_clave': status_clave,
            'meta': json.dumps(meta) if meta else None
        }
        
        event_id = self.db.execute_insert(query, params)
        print(f'[Movimiento Model] Evento de obstáculo registrado: ID {event_id}')
        return event_id
    
    def get_device_events(self, device_id, limit=50, event_type=None):
        """
        Obtiene el historial de eventos de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            limit (int): Número máximo de eventos a retornar
            event_type (str, optional): Filtrar por tipo ('movement', 'obstacle', 'demo')
        
        Returns:
            list: Lista de eventos
        """
        where_clause = "device_id = %(device_id)s"
        params = {'device_id': device_id, 'limit': limit}
        
        if event_type:
            where_clause += " AND event_type = %(event_type)s"
            params['event_type'] = event_type
        
        query = f"""
        SELECT 
            de.id,
            de.device_id,
            de.event_type,
            de.status_clave,
            de.demo_id,
            de.event_ts,
            de.meta,
            CASE 
                WHEN de.event_type = 'movement' THEN ops.status_texto
                WHEN de.event_type = 'obstacle' THEN obs.status_texto
                ELSE NULL
            END as status_description
        FROM device_events de
        LEFT JOIN op_status ops ON de.event_type = 'movement' AND de.status_clave = ops.status_clave
        LEFT JOIN obstacle_status obs ON de.event_type = 'obstacle' AND de.status_clave = obs.status_clave
        WHERE {where_clause}
        ORDER BY de.event_ts DESC
        LIMIT %(limit)s
        """
        
        results = self.db.execute_query(query, params, fetch_all=True)
        
        # Parsear el campo meta de JSON string a dict
        for event in results:
            if event.get('meta'):
                try:
                    event['meta'] = json.loads(event['meta'])
                except:
                    pass
        
        return results
    
    def get_all_op_status(self):
        """
        Obtiene todos los estados operacionales disponibles
        
        Returns:
            list: Lista de estados operacionales
        """
        query = """
        SELECT 
            status_clave,
            status_texto,
            description
        FROM op_status
        ORDER BY status_clave
        """
        
        results = self.db.execute_query(query, fetch_all=True)
        return results
    
    def get_all_obstacle_status(self):
        """
        Obtiene todos los estados de obstáculos disponibles
        
        Returns:
            list: Lista de estados de obstáculos
        """
        query = """
        SELECT 
            status_clave,
            status_texto,
            description
        FROM obstacle_status
        ORDER BY status_clave
        """
        
        results = self.db.execute_query(query, fetch_all=True)
        return results
    
    def get_last_movement(self, device_id):
        """
        Obtiene el último movimiento registrado de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            dict: Último evento de movimiento o None
        """
        query = """
        SELECT 
            de.id,
            de.device_id,
            de.status_clave,
            de.event_ts,
            de.meta,
            ops.status_texto,
            ops.description
        FROM device_events de
        INNER JOIN op_status ops ON de.status_clave = ops.status_clave
        WHERE de.device_id = %(device_id)s 
        AND de.event_type = 'movement'
        ORDER BY de.event_ts DESC
        LIMIT 1
        """
        
        result = self.db.execute_query(
            query,
            {'device_id': device_id},
            fetch_one=True
        )
        
        if result and result.get('meta'):
            try:
                result['meta'] = json.loads(result['meta'])
            except:
                pass
        
        return result
    
    def get_recent_obstacles(self, device_id, minutes=30):
        """
        Obtiene obstáculos detectados recientemente
        
        Args:
            device_id (int): ID del dispositivo
            minutes (int): Ventana de tiempo en minutos
        
        Returns:
            list: Lista de eventos de obstáculos recientes
        """
        query = """
        SELECT 
            de.id,
            de.device_id,
            de.status_clave,
            de.event_ts,
            de.meta,
            obs.status_texto,
            obs.description
        FROM device_events de
        INNER JOIN obstacle_status obs ON de.status_clave = obs.status_clave
        WHERE de.device_id = %(device_id)s 
        AND de.event_type = 'obstacle'
        AND de.event_ts >= NOW() - INTERVAL %(minutes)s MINUTE
        ORDER BY de.event_ts DESC
        """
        
        results = self.db.execute_query(
            query,
            {'device_id': device_id, 'minutes': minutes},
            fetch_all=True
        )
        
        for event in results:
            if event.get('meta'):
                try:
                    event['meta'] = json.loads(event['meta'])
                except:
                    pass
        
        return results
    
    def get_movement_statistics(self, device_id, days=7):
        """
        Obtiene estadísticas de movimiento de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            days (int): Número de días hacia atrás
        
        Returns:
            dict: Estadísticas de movimiento
        """
        query = """
        SELECT 
            ops.status_texto,
            COUNT(*) as count,
            MIN(de.event_ts) as first_occurrence,
            MAX(de.event_ts) as last_occurrence
        FROM device_events de
        INNER JOIN op_status ops ON de.status_clave = ops.status_clave
        WHERE de.device_id = %(device_id)s 
        AND de.event_type = 'movement'
        AND de.event_ts >= NOW() - INTERVAL %(days)s DAY
        GROUP BY ops.status_texto, ops.status_clave
        ORDER BY count DESC
        """
        
        results = self.db.execute_query(
            query,
            {'device_id': device_id, 'days': days},
            fetch_all=True
        )
        
        return results
    
    def delete_old_events(self, days=30):
        """
        Elimina eventos antiguos para limpieza de base de datos
        
        Args:
            days (int): Eliminar eventos más antiguos que X días
        
        Returns:
            int: Número de eventos eliminados
        """
        query = """
        DELETE FROM device_events
        WHERE event_ts < NOW() - INTERVAL %(days)s DAY
        """
        
        affected_rows = self.db.execute_delete(query, {'days': days})
        print(f'[Movimiento Model] {affected_rows} eventos antiguos eliminados')
        return affected_rows
    
    def validate_command(self, command):
        """
        Valida que un comando de movimiento sea válido
        
        Args:
            command (str): Comando a validar
        
        Returns:
            bool: True si el comando es válido
        """
        return command in self.MOVEMENT_COMMANDS
    
    def get_command_code(self, command):
        """
        Obtiene el código numérico de un comando
        
        Args:
            command (str): Nombre del comando
        
        Returns:
            int: Código del comando o None si no existe
        """
        return self.MOVEMENT_COMMANDS.get(command)
