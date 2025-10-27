"""
Modelo: Carrito (Device)
Representa un dispositivo carrito IoT registrado en el sistema
Incluye métodos para CRUD y geolocalización
"""

from datetime import datetime


class Carrito:
    """
    Clase que representa un dispositivo carrito en el sistema
    Mapea la tabla 'devices' de la base de datos
    """
    
    def __init__(self, db):
        """
        Inicializa el modelo con la conexión a base de datos
        
        Args:
            db (Database): Instancia de la clase Database
        """
        self.db = db
        self.table_name = 'devices'
    
    def create(self, device_data):
        """
        Registra un nuevo dispositivo en la base de datos
        
        Args:
            device_data (dict): Diccionario con datos del dispositivo
                - device_name (str): Nombre del dispositivo
                - client_ip (str): IP del cliente
                - country (str, optional): País
                - city (str, optional): Ciudad
                - latitude (float, optional): Latitud
                - longitude (float, optional): Longitud
        
        Returns:
            int: ID del dispositivo creado
        """
        query = """
        INSERT INTO devices (
            device_name, 
            client_ip, 
            country, 
            city, 
            latitude, 
            longitude,
            created_at
        ) VALUES (
            %(device_name)s,
            %(client_ip)s,
            %(country)s,
            %(city)s,
            %(latitude)s,
            %(longitude)s,
            NOW()
        )
        """
        
        params = {
            'device_name': device_data.get('device_name'),
            'client_ip': device_data.get('client_ip'),
            'country': device_data.get('country'),
            'city': device_data.get('city'),
            'latitude': device_data.get('latitude'),
            'longitude': device_data.get('longitude')
        }
        
        device_id = self.db.execute_insert(query, params)
        print(f'[Carrito Model] Dispositivo creado con ID: {device_id}')
        return device_id
    
    def get_by_id(self, device_id):
        """
        Obtiene un dispositivo por su ID
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            dict: Datos del dispositivo o None si no existe
        """
        query = """
        SELECT 
            id,
            device_name,
            client_ip,
            country,
            city,
            latitude,
            longitude,
            created_at,
            updated_at
        FROM devices
        WHERE id = %(device_id)s
        """
        
        result = self.db.execute_query(
            query, 
            {'device_id': device_id}, 
            fetch_one=True
        )
        
        return result
    
    def get_all(self, limit=100, offset=0):
        """
        Obtiene todos los dispositivos registrados con paginación
        
        Args:
            limit (int): Número máximo de resultados
            offset (int): Desplazamiento para paginación
        
        Returns:
            list: Lista de dispositivos
        """
        query = """
        SELECT 
            id,
            device_name,
            client_ip,
            country,
            city,
            latitude,
            longitude,
            created_at,
            updated_at
        FROM devices
        ORDER BY created_at DESC
        LIMIT %(limit)s OFFSET %(offset)s
        """
        
        results = self.db.execute_query(
            query,
            {'limit': limit, 'offset': offset},
            fetch_all=True
        )
        
        return results
    
    def update(self, device_id, device_data):
        """
        Actualiza los datos de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            device_data (dict): Datos a actualizar
        
        Returns:
            int: Número de filas afectadas
        """
        # Construir query dinámicamente basado en los campos proporcionados
        update_fields = []
        params = {'device_id': device_id}
        
        allowed_fields = ['device_name', 'client_ip', 'country', 'city', 'latitude', 'longitude']
        
        for field in allowed_fields:
            if field in device_data:
                update_fields.append(f"{field} = %({field})s")
                params[field] = device_data[field]
        
        if not update_fields:
            return 0
        
        update_fields.append("updated_at = NOW()")
        
        query = f"""
        UPDATE devices
        SET {', '.join(update_fields)}
        WHERE id = %(device_id)s
        """
        
        affected_rows = self.db.execute_update(query, params)
        print(f'[Carrito Model] Dispositivo {device_id} actualizado, {affected_rows} filas afectadas')
        return affected_rows
    
    def delete(self, device_id):
        """
        Elimina un dispositivo (soft delete recomendado en producción)
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            int: Número de filas eliminadas
        """
        query = """
        DELETE FROM devices
        WHERE id = %(device_id)s
        """
        
        affected_rows = self.db.execute_delete(query, {'device_id': device_id})
        print(f'[Carrito Model] Dispositivo {device_id} eliminado')
        return affected_rows
    
    def get_by_ip(self, client_ip):
        """
        Busca dispositivos por IP del cliente
        
        Args:
            client_ip (str): IP del cliente
        
        Returns:
            list: Lista de dispositivos con esa IP
        """
        query = """
        SELECT 
            id,
            device_name,
            client_ip,
            country,
            city,
            latitude,
            longitude,
            created_at,
            updated_at
        FROM devices
        WHERE client_ip = %(client_ip)s
        ORDER BY created_at DESC
        """
        
        results = self.db.execute_query(
            query,
            {'client_ip': client_ip},
            fetch_all=True
        )
        
        return results
    
    def get_by_location(self, country=None, city=None):
        """
        Busca dispositivos por ubicación geográfica
        
        Args:
            country (str, optional): País
            city (str, optional): Ciudad
        
        Returns:
            list: Lista de dispositivos en esa ubicación
        """
        conditions = []
        params = {}
        
        if country:
            conditions.append("country = %(country)s")
            params['country'] = country
        
        if city:
            conditions.append("city = %(city)s")
            params['city'] = city
        
        if not conditions:
            return self.get_all()
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            id,
            device_name,
            client_ip,
            country,
            city,
            latitude,
            longitude,
            created_at,
            updated_at
        FROM devices
        WHERE {where_clause}
        ORDER BY created_at DESC
        """
        
        results = self.db.execute_query(query, params, fetch_all=True)
        return results
    
    def count_total(self):
        """
        Cuenta el total de dispositivos registrados
        
        Returns:
            int: Número total de dispositivos
        """
        query = "SELECT COUNT(*) as total FROM devices"
        result = self.db.execute_query(query, fetch_one=True)
        return result['total'] if result else 0
    
    def get_online_devices(self, minutes=5):
        """
        Obtiene dispositivos que han tenido actividad reciente
        Se considera "online" si tuvo actividad en los últimos X minutos
        
        Args:
            minutes (int): Minutos para considerar dispositivo online
        
        Returns:
            list: Lista de dispositivos online
        """
        query = """
        SELECT DISTINCT
            d.id,
            d.device_name,
            d.client_ip,
            d.country,
            d.city,
            MAX(de.event_ts) as last_activity
        FROM devices d
        INNER JOIN device_events de ON d.id = de.device_id
        WHERE de.event_ts >= NOW() - INTERVAL %(minutes)s MINUTE
        GROUP BY d.id, d.device_name, d.client_ip, d.country, d.city
        ORDER BY last_activity DESC
        """
        
        results = self.db.execute_query(
            query,
            {'minutes': minutes},
            fetch_all=True
        )
        
        return results
