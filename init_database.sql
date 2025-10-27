"""
Script SQL para inicializar la base de datos en AWS Aurora RDS
Ejecutar este script para crear todas las tablas necesarias
"""

-- =====================================================
-- BASE DE DATOS
-- =====================================================
CREATE DATABASE IF NOT EXISTS carrito_iot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE carrito_iot;

-- =====================================================
-- TABLA: devices
-- Almacena información de los dispositivos (carritos) registrados
-- =====================================================
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    client_ip VARCHAR(45) NOT NULL COMMENT 'Soporta IPv4 y IPv6',
    country VARCHAR(100),
    city VARCHAR(100),
    latitude DECIMAL(10,7) COMMENT 'Coordenada geográfica',
    longitude DECIMAL(10,7) COMMENT 'Coordenada geográfica',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_client_ip (client_ip),
    INDEX idx_location (country, city),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Dispositivos (carritos) registrados en el sistema';

-- =====================================================
-- TABLA: op_status
-- Estados operacionales para movimientos del carrito
-- =====================================================
CREATE TABLE IF NOT EXISTS op_status (
    status_clave INT PRIMARY KEY,
    status_texto VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de estados operacionales (comandos de movimiento)';

-- Insertar estados operacionales iniciales
INSERT INTO op_status (status_clave, status_texto, description) VALUES
(1, 'forward', 'Movimiento hacia adelante'),
(2, 'backward', 'Movimiento hacia atrás'),
(3, 'left', 'Giro a la izquierda'),
(4, 'right', 'Giro a la derecha'),
(5, 'stop', 'Detención completa del carrito'),
(6, 'rotate_left', 'Rotación 360° hacia la izquierda'),
(7, 'rotate_right', 'Rotación 360° hacia la derecha'),
(8, 'forward_left', 'Movimiento adelante con giro izquierda'),
(9, 'forward_right', 'Movimiento adelante con giro derecha'),
(10, 'backward_left', 'Movimiento atrás con giro izquierda'),
(11, 'backward_right', 'Movimiento atrás con giro derecha')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- =====================================================
-- TABLA: obstacle_status
-- Estados de detección de obstáculos
-- =====================================================
CREATE TABLE IF NOT EXISTS obstacle_status (
    status_clave INT PRIMARY KEY,
    status_texto VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Catálogo de estados de detección de obstáculos';

-- Insertar estados de obstáculos iniciales
INSERT INTO obstacle_status (status_clave, status_texto, description) VALUES
(1, 'obstacle_detected', 'Obstáculo detectado en el camino'),
(2, 'obstacle_front', 'Obstáculo detectado al frente'),
(3, 'obstacle_left', 'Obstáculo detectado a la izquierda'),
(4, 'obstacle_right', 'Obstáculo detectado a la derecha'),
(5, 'obstacle_rear', 'Obstáculo detectado atrás'),
(6, 'path_clear', 'Camino despejado, sin obstáculos')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- =====================================================
-- TABLA: device_events
-- Historial de eventos (movimientos y obstáculos)
-- =====================================================
CREATE TABLE IF NOT EXISTS device_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    event_type ENUM('movement','obstacle','demo') NOT NULL,
    status_clave INT NOT NULL COMMENT 'FK a op_status o obstacle_status según event_type',
    demo_id INT DEFAULT NULL COMMENT 'ID del demo si el evento proviene de una demostración',
    event_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    meta JSON COMMENT 'Metadatos adicionales: velocidad, duración, IP origen, distancia sensor, etc.',
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    
    INDEX idx_device_type (device_id, event_type),
    INDEX idx_event_ts (event_ts),
    INDEX idx_demo (demo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Registro de todos los eventos del carrito (movimientos, obstáculos, demos)';

-- =====================================================
-- TABLA: demos
-- Demostraciones pregrabadas de movimientos
-- =====================================================
CREATE TABLE IF NOT EXISTS demos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Demostraciones programadas de secuencias de movimientos';

-- =====================================================
-- TABLA: demo_moves
-- Movimientos individuales de una demostración
-- =====================================================
CREATE TABLE IF NOT EXISTS demo_moves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    demo_id INT NOT NULL,
    move_order INT NOT NULL COMMENT 'Orden de ejecución en la secuencia',
    status_clave INT NOT NULL COMMENT 'FK a op_status.status_clave',
    duration_ms INT NOT NULL COMMENT 'Duración del movimiento en milisegundos',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (demo_id) REFERENCES demos(id) ON DELETE CASCADE,
    FOREIGN KEY (status_clave) REFERENCES op_status(status_clave),
    
    INDEX idx_demo_order (demo_id, move_order),
    UNIQUE KEY unique_demo_order (demo_id, move_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Secuencia de movimientos de cada demostración';

-- =====================================================
-- TABLA: scheduled_demo_runs
-- Ejecuciones programadas de demostraciones
-- =====================================================
CREATE TABLE IF NOT EXISTS scheduled_demo_runs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    demo_id INT NOT NULL,
    run_at DATETIME NOT NULL COMMENT 'Fecha y hora de ejecución programada',
    runs_count INT DEFAULT 1 COMMENT 'Número de veces que se ejecutará',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    executed BOOLEAN DEFAULT FALSE,
    executed_at DATETIME DEFAULT NULL,
    
    FOREIGN KEY (demo_id) REFERENCES demos(id) ON DELETE CASCADE,
    INDEX idx_run_at (run_at),
    INDEX idx_executed (executed)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Programación de ejecuciones de demostraciones';

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista: Eventos recientes con información completa
CREATE OR REPLACE VIEW v_recent_events AS
SELECT 
    de.id,
    de.device_id,
    d.device_name,
    de.event_type,
    de.event_ts,
    CASE 
        WHEN de.event_type = 'movement' THEN ops.status_texto
        WHEN de.event_type = 'obstacle' THEN obs.status_texto
        ELSE 'demo'
    END as status_description,
    de.meta
FROM device_events de
INNER JOIN devices d ON de.device_id = d.id
LEFT JOIN op_status ops ON de.event_type = 'movement' AND de.status_clave = ops.status_clave
LEFT JOIN obstacle_status obs ON de.event_type = 'obstacle' AND de.status_clave = obs.status_clave
ORDER BY de.event_ts DESC
LIMIT 100;

-- Vista: Estadísticas por dispositivo
CREATE OR REPLACE VIEW v_device_stats AS
SELECT 
    d.id,
    d.device_name,
    COUNT(de.id) as total_events,
    SUM(CASE WHEN de.event_type = 'movement' THEN 1 ELSE 0 END) as movement_events,
    SUM(CASE WHEN de.event_type = 'obstacle' THEN 1 ELSE 0 END) as obstacle_events,
    MAX(de.event_ts) as last_activity
FROM devices d
LEFT JOIN device_events de ON d.id = de.device_id
GROUP BY d.id, d.device_name;

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

DELIMITER //

-- Procedimiento: Limpiar eventos antiguos
CREATE PROCEDURE sp_cleanup_old_events(IN days_old INT)
BEGIN
    DELETE FROM device_events
    WHERE event_ts < DATE_SUB(NOW(), INTERVAL days_old DAY);
    
    SELECT ROW_COUNT() as deleted_rows;
END //

-- Procedimiento: Obtener último estado del dispositivo
CREATE PROCEDURE sp_get_device_last_status(IN p_device_id INT)
BEGIN
    SELECT 
        de.event_type,
        ops.status_texto as movement_status,
        de.event_ts,
        de.meta
    FROM device_events de
    LEFT JOIN op_status ops ON de.status_clave = ops.status_clave
    WHERE de.device_id = p_device_id
    AND de.event_type = 'movement'
    ORDER BY de.event_ts DESC
    LIMIT 1;
END //

DELIMITER ;

-- =====================================================
-- ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- =====================================================

-- Índice compuesto para búsquedas frecuentes
ALTER TABLE device_events ADD INDEX idx_device_event_ts (device_id, event_ts DESC);

-- Índice para búsquedas por tipo de evento
ALTER TABLE device_events ADD INDEX idx_event_type_ts (event_type, event_ts DESC);

-- =====================================================
-- PERMISOS Y USUARIOS
-- =====================================================

-- Crear usuario para la aplicación (ajustar según necesidades)
-- CREATE USER 'carrito_app'@'%' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON carrito_iot.* TO 'carrito_app'@'%';
-- FLUSH PRIVILEGES;

-- =====================================================
-- SCRIPT COMPLETADO
-- =====================================================
SELECT 'Base de datos carrito_iot inicializada exitosamente!' as message;
