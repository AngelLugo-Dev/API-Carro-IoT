"""
Utilidades auxiliares para el backend
Este módulo contendrá funciones helper reutilizables
"""

import hashlib
import secrets
import string
from datetime import datetime, timedelta
import json


def generate_token(length=32):
    """
    Genera un token aleatorio seguro
    
    Args:
        length (int): Longitud del token
    
    Returns:
        str: Token aleatorio
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_string(text):
    """
    Genera un hash SHA256 de un string
    
    Args:
        text (str): Texto a hashear
    
    Returns:
        str: Hash hexadecimal
    """
    return hashlib.sha256(text.encode()).hexdigest()


def format_timestamp(dt=None):
    """
    Formatea un timestamp al formato ISO 8601
    
    Args:
        dt (datetime, optional): Datetime a formatear. Si None, usa ahora.
    
    Returns:
        str: Timestamp formateado
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def parse_json_safe(json_str):
    """
    Parsea JSON de forma segura
    
    Args:
        json_str (str): String JSON a parsear
    
    Returns:
        dict: Objeto parseado o None si hay error
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def validate_coordinates(latitude, longitude):
    """
    Valida coordenadas geográficas
    
    Args:
        latitude (float): Latitud
        longitude (float): Longitud
    
    Returns:
        bool: True si son válidas
    """
    try:
        lat = float(latitude)
        lon = float(longitude)
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def get_time_ago(dt):
    """
    Obtiene el tiempo transcurrido desde una fecha
    
    Args:
        dt (datetime): Fecha de referencia
    
    Returns:
        str: Descripción del tiempo transcurrido
    """
    if not isinstance(dt, datetime):
        return "N/A"
    
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} segundos"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutos"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} horas"
    else:
        return f"{int(seconds / 86400)} días"


def sanitize_string(text, max_length=255):
    """
    Sanitiza un string para prevenir inyecciones
    
    Args:
        text (str): Texto a sanitizar
        max_length (int): Longitud máxima
    
    Returns:
        str: Texto sanitizado
    """
    if not isinstance(text, str):
        return ""
    
    # Remover caracteres peligrosos
    sanitized = text.strip()
    sanitized = sanitized.replace('<', '').replace('>', '')
    sanitized = sanitized.replace(';', '').replace('--', '')
    
    # Limitar longitud
    return sanitized[:max_length]


def chunk_list(lst, chunk_size):
    """
    Divide una lista en chunks de tamaño específico
    
    Args:
        lst (list): Lista a dividir
        chunk_size (int): Tamaño de cada chunk
    
    Returns:
        list: Lista de chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class ResponseFormatter:
    """
    Clase helper para formatear respuestas API de forma consistente
    """
    
    @staticmethod
    def success(data=None, message="Success", **kwargs):
        """
        Formatea una respuesta exitosa
        
        Args:
            data: Datos a retornar
            message (str): Mensaje
            **kwargs: Datos adicionales
        
        Returns:
            dict: Respuesta formateada
        """
        response = {
            'success': True,
            'message': message,
            'timestamp': format_timestamp()
        }
        
        if data is not None:
            response['data'] = data
        
        response.update(kwargs)
        return response
    
    @staticmethod
    def error(message="Error", code=None, **kwargs):
        """
        Formatea una respuesta de error
        
        Args:
            message (str): Mensaje de error
            code (str, optional): Código de error
            **kwargs: Datos adicionales
        
        Returns:
            dict: Respuesta de error formateada
        """
        response = {
            'success': False,
            'error': message,
            'timestamp': format_timestamp()
        }
        
        if code:
            response['error_code'] = code
        
        response.update(kwargs)
        return response
