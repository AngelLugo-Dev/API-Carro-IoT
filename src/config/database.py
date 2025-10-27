"""
Configuración de Base de Datos
Conexión a AWS Aurora RDS MySQL
Patrón Singleton para gestión de conexión
"""

import pymysql
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Cargar variables de entorno
load_dotenv()


class Database:
    """
    Clase para gestionar la conexión a AWS Aurora RDS
    Implementa patrón Singleton para reutilizar conexión
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        """
        Implementación del patrón Singleton
        """
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Inicializa la configuración de base de datos desde variables de entorno
        """
        if not hasattr(self, 'initialized'):
            self.config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'carrito_iot'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor,
                'autocommit': False
            }
            self.initialized = True
            print(f'[Database] Configuración cargada para: {self.config["host"]}:{self.config["port"]}')
    
    def get_connection(self):
        """
        Obtiene una nueva conexión a la base de datos
        Returns:
            pymysql.Connection: Objeto de conexión activa
        """
        try:
            connection = pymysql.connect(**self.config)
            print('[Database] Conexión establecida exitosamente')
            return connection
        except pymysql.Error as e:
            print(f'[Database] Error al conectar: {e}')
            raise
    
    @contextmanager
    def get_cursor(self):
        """
        Context manager para obtener cursor y manejar transacciones automáticamente
        Uso:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM devices")
                results = cursor.fetchall()
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f'[Database] Error en transacción, rollback ejecutado: {e}')
            raise
        finally:
            cursor.close()
            connection.close()
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=True):
        """
        Ejecuta una consulta SQL y retorna resultados
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple/dict): Parámetros para la consulta
            fetch_one (bool): Si True, retorna solo un resultado
            fetch_all (bool): Si True, retorna todos los resultados
            
        Returns:
            dict/list: Resultados de la consulta
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.lastrowid
    
    def execute_insert(self, query, params=None):
        """
        Ejecuta un INSERT y retorna el ID insertado
        
        Args:
            query (str): Consulta INSERT
            params (tuple/dict): Parámetros para la consulta
            
        Returns:
            int: ID del registro insertado
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query, params=None):
        """
        Ejecuta un UPDATE y retorna el número de filas afectadas
        
        Args:
            query (str): Consulta UPDATE
            params (tuple/dict): Parámetros para la consulta
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_cursor() as cursor:
            affected_rows = cursor.execute(query, params)
            return affected_rows
    
    def execute_delete(self, query, params=None):
        """
        Ejecuta un DELETE y retorna el número de filas eliminadas
        
        Args:
            query (str): Consulta DELETE
            params (tuple/dict): Parámetros para la consulta
            
        Returns:
            int: Número de filas eliminadas
        """
        with self.get_cursor() as cursor:
            affected_rows = cursor.execute(query, params)
            return affected_rows
    
    def check_connection(self):
        """
        Verifica que la conexión a la base de datos esté funcionando
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f'[Database] Error en check_connection: {e}')
            return False
    
    def execute_many(self, query, params_list):
        """
        Ejecuta múltiples inserts/updates en una sola transacción
        
        Args:
            query (str): Consulta SQL
            params_list (list): Lista de tuplas con parámetros
            
        Returns:
            int: Número de filas afectadas
        """
        with self.get_cursor() as cursor:
            affected_rows = cursor.executemany(query, params_list)
            return affected_rows
    
    def call_procedure(self, proc_name, params=None):
        """
        Ejecuta un stored procedure
        
        Args:
            proc_name (str): Nombre del procedimiento
            params (tuple): Parámetros del procedimiento
            
        Returns:
            list: Resultados del procedimiento
        """
        with self.get_cursor() as cursor:
            cursor.callproc(proc_name, params)
            return cursor.fetchall()


# Instancia global del Database (Singleton)
db_instance = Database()
