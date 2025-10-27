"""
Controlador: Carrito
Gestiona la lógica de negocio para dispositivos carrito
Capa intermedia entre las rutas y el modelo
"""

from models.carrito import Carrito
from datetime import datetime


class CarritoController:
    """
    Controlador para gestionar operaciones de dispositivos carrito
    Implementa lógica de negocio y validaciones
    """
    
    def __init__(self, db):
        """
        Inicializa el controlador con la conexión a base de datos
        
        Args:
            db (Database): Instancia de la clase Database
        """
        self.carrito_model = Carrito(db)
        print('[CarritoController] Controlador inicializado')
    
    def register_device(self, device_data):
        """
        Registra un nuevo dispositivo con validaciones
        
        Args:
            device_data (dict): Datos del dispositivo a registrar
                - device_name (str, required): Nombre del dispositivo
                - client_ip (str, required): IP del cliente
                - country (str, optional): País
                - city (str, optional): Ciudad
                - latitude (float, optional): Latitud
                - longitude (float, optional): Longitud
        
        Returns:
            int: ID del dispositivo registrado
        
        Raises:
            ValueError: Si faltan campos requeridos o datos inválidos
        """
        # Validar campos requeridos
        if not device_data.get('device_name'):
            raise ValueError('device_name es requerido')
        
        if not device_data.get('client_ip'):
            raise ValueError('client_ip es requerido')
        
        # Validar formato de IP (básico)
        client_ip = device_data.get('client_ip')
        if not self._validate_ip(client_ip):
            raise ValueError('Formato de IP inválido')
        
        # Validar coordenadas si están presentes
        latitude = device_data.get('latitude')
        longitude = device_data.get('longitude')
        
        if latitude is not None:
            if not (-90 <= float(latitude) <= 90):
                raise ValueError('Latitud debe estar entre -90 y 90')
        
        if longitude is not None:
            if not (-180 <= float(longitude) <= 180):
                raise ValueError('Longitud debe estar entre -180 y 180')
        
        # Verificar si ya existe un dispositivo con el mismo nombre
        existing_devices = self.carrito_model.get_all()
        for device in existing_devices:
            if device['device_name'] == device_data['device_name']:
                print(f'[CarritoController] Advertencia: Ya existe dispositivo con nombre {device_data["device_name"]}')
        
        # Registrar dispositivo
        device_id = self.carrito_model.create(device_data)
        
        print(f'[CarritoController] Dispositivo registrado exitosamente: ID {device_id}')
        return device_id
    
    def get_device_by_id(self, device_id):
        """
        Obtiene un dispositivo por su ID
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            dict: Datos del dispositivo o None
        """
        if not isinstance(device_id, int) or device_id <= 0:
            raise ValueError('device_id debe ser un entero positivo')
        
        device = self.carrito_model.get_by_id(device_id)
        
        if device:
            # Convertir datetime a string para JSON
            device = self._serialize_device(device)
            print(f'[CarritoController] Dispositivo {device_id} encontrado')
        else:
            print(f'[CarritoController] Dispositivo {device_id} no encontrado')
        
        return device
    
    def get_all_devices(self, limit=100, offset=0):
        """
        Obtiene todos los dispositivos con paginación
        
        Args:
            limit (int): Número máximo de resultados
            offset (int): Desplazamiento para paginación
        
        Returns:
            list: Lista de dispositivos serializados
        """
        devices = self.carrito_model.get_all(limit=limit, offset=offset)
        
        # Serializar dispositivos
        serialized_devices = [self._serialize_device(device) for device in devices]
        
        print(f'[CarritoController] {len(serialized_devices)} dispositivos obtenidos')
        return serialized_devices
    
    def update_device(self, device_id, device_data):
        """
        Actualiza los datos de un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
            device_data (dict): Datos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar que el dispositivo existe
        existing_device = self.carrito_model.get_by_id(device_id)
        if not existing_device:
            raise ValueError(f'Dispositivo {device_id} no encontrado')
        
        # Validar coordenadas si están presentes
        if 'latitude' in device_data:
            latitude = float(device_data['latitude'])
            if not (-90 <= latitude <= 90):
                raise ValueError('Latitud debe estar entre -90 y 90')
        
        if 'longitude' in device_data:
            longitude = float(device_data['longitude'])
            if not (-180 <= longitude <= 180):
                raise ValueError('Longitud debe estar entre -180 y 180')
        
        # Validar IP si está presente
        if 'client_ip' in device_data:
            if not self._validate_ip(device_data['client_ip']):
                raise ValueError('Formato de IP inválido')
        
        # Actualizar dispositivo
        affected_rows = self.carrito_model.update(device_id, device_data)
        
        success = affected_rows > 0
        if success:
            print(f'[CarritoController] Dispositivo {device_id} actualizado exitosamente')
        
        return success
    
    def delete_device(self, device_id):
        """
        Elimina un dispositivo
        
        Args:
            device_id (int): ID del dispositivo
        
        Returns:
            bool: True si se eliminó correctamente
        """
        # Validar que el dispositivo existe
        existing_device = self.carrito_model.get_by_id(device_id)
        if not existing_device:
            raise ValueError(f'Dispositivo {device_id} no encontrado')
        
        # Eliminar dispositivo
        affected_rows = self.carrito_model.delete(device_id)
        
        success = affected_rows > 0
        if success:
            print(f'[CarritoController] Dispositivo {device_id} eliminado exitosamente')
        
        return success
    
    def get_devices_by_location(self, country=None, city=None):
        """
        Obtiene dispositivos filtrados por ubicación
        
        Args:
            country (str, optional): País
            city (str, optional): Ciudad
        
        Returns:
            list: Lista de dispositivos en esa ubicación
        """
        devices = self.carrito_model.get_by_location(country=country, city=city)
        serialized_devices = [self._serialize_device(device) for device in devices]
        
        print(f'[CarritoController] {len(serialized_devices)} dispositivos encontrados en ubicación')
        return serialized_devices
    
    def get_devices_by_ip(self, client_ip):
        """
        Obtiene dispositivos por IP
        
        Args:
            client_ip (str): IP del cliente
        
        Returns:
            list: Lista de dispositivos con esa IP
        """
        if not self._validate_ip(client_ip):
            raise ValueError('Formato de IP inválido')
        
        devices = self.carrito_model.get_by_ip(client_ip)
        serialized_devices = [self._serialize_device(device) for device in devices]
        
        print(f'[CarritoController] {len(serialized_devices)} dispositivos encontrados con IP {client_ip}')
        return serialized_devices
    
    def get_total_devices_count(self):
        """
        Obtiene el conteo total de dispositivos
        
        Returns:
            int: Número total de dispositivos
        """
        count = self.carrito_model.count_total()
        print(f'[CarritoController] Total de dispositivos: {count}')
        return count
    
    def get_online_devices(self, minutes=5):
        """
        Obtiene dispositivos con actividad reciente
        
        Args:
            minutes (int): Ventana de tiempo en minutos
        
        Returns:
            list: Lista de dispositivos online
        """
        devices = self.carrito_model.get_online_devices(minutes=minutes)
        serialized_devices = [self._serialize_device(device) for device in devices]
        
        print(f'[CarritoController] {len(serialized_devices)} dispositivos online')
        return serialized_devices
    
    def _validate_ip(self, ip):
        """
        Valida formato de dirección IP (IPv4 o IPv6 básico)
        
        Args:
            ip (str): Dirección IP a validar
        
        Returns:
            bool: True si es válida
        """
        if not ip:
            return False
        
        # Validación básica IPv4
        parts = ip.split('.')
        if len(parts) == 4:
            try:
                return all(0 <= int(part) <= 255 for part in parts)
            except ValueError:
                pass
        
        # IPv6 básico (solo verificar que contenga ':')
        if ':' in ip:
            return True
        
        return False
    
    def _serialize_device(self, device):
        """
        Serializa un dispositivo convirtiendo datetime a string
        
        Args:
            device (dict): Dispositivo a serializar
        
        Returns:
            dict: Dispositivo serializado
        """
        if not device:
            return None
        
        serialized = device.copy()
        
        # Convertir datetime a ISO format string
        if isinstance(serialized.get('created_at'), datetime):
            serialized['created_at'] = serialized['created_at'].isoformat()
        
        if isinstance(serialized.get('updated_at'), datetime):
            serialized['updated_at'] = serialized['updated_at'].isoformat()
        
        # Convertir Decimal a float para coordenadas
        if serialized.get('latitude'):
            serialized['latitude'] = float(serialized['latitude'])
        
        if serialized.get('longitude'):
            serialized['longitude'] = float(serialized['longitude'])
        
        return serialized
