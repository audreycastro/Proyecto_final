-- Crear base de datos
DROP DATABASE IF EXISTS seguridad_mexico;
CREATE DATABASE seguridad_mexico;
USE seguridad_mexico;

-- Tabla: estados
CREATE TABLE estados (
    id_estado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: tipos_delito
CREATE TABLE tipos_delito (
    id_tipo_delito INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    subtipo VARCHAR(200),
    modalidad VARCHAR(200),
    categoria VARCHAR(50),
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: incidencia_delictiva
CREATE TABLE incidencia_delictiva (
    id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL,
    mes VARCHAR(20) NOT NULL,
    mes_num INT NOT NULL,
    id_estado INT NOT NULL,
    id_tipo_delito INT NOT NULL,
    cantidad INT NOT NULL,
    fecha VARCHAR(10),
    periodo VARCHAR(50),
    porcentaje_estado DECIMAL(10,4),
    cantidad_normalizada DECIMAL(10,6),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
    FOREIGN KEY (id_tipo_delito) REFERENCES tipos_delito(id_tipo_delito),
    INDEX idx_anio (anio),
    INDEX idx_mes (mes_num),
    INDEX idx_estado (id_estado),
    INDEX idx_tipo_delito (id_tipo_delito),
    INDEX idx_fecha (fecha)
);

-- Tabla: percepcion_seguridad
CREATE TABLE percepcion_seguridad (
    id_percepcion INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL,
    id_estado INT NOT NULL,
    percepcion_inseguridad DECIMAL(5,2) NOT NULL,
    total_delitos INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
    INDEX idx_anio_estado (anio, id_estado)
);

-- Tabla: estadisticas_agregadas
CREATE TABLE estadisticas_agregadas (
    id_estadistica INT AUTO_INCREMENT PRIMARY KEY,
    tipo_agregacion VARCHAR(50) NOT NULL,
    anio INT,
    mes_num INT,
    id_estado INT,
    id_tipo_delito INT,
    total_delitos INT,
    promedio_delitos DECIMAL(10,2),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_estado) REFERENCES estados(id_estado),
    FOREIGN KEY (id_tipo_delito) REFERENCES tipos_delito(id_tipo_delito),
    INDEX idx_tipo_agregacion (tipo_agregacion),
    INDEX idx_anio (anio)
);


-- VISTAS PARA ANALISIS


-- Vista: Incidencia con nombres completos
CREATE VIEW v_incidencia_completa AS
SELECT 
    i.id_incidencia,
    i.anio,
    i.mes,
    i.mes_num,
    e.nombre AS estado,
    t.nombre AS tipo_delito,
    t.subtipo,
    t.modalidad,
    t.categoria AS categoria_delito,
    i.cantidad,
    i.fecha,
    i.periodo,
    i.porcentaje_estado,
    i.cantidad_normalizada
FROM incidencia_delictiva i
JOIN estados e ON i.id_estado = e.id_estado
JOIN tipos_delito t ON i.id_tipo_delito = t.id_tipo_delito;

-- Vista: Total de delitos por estado y año
CREATE VIEW v_delitos_por_estado_anio AS
SELECT 
    e.nombre AS estado,
    i.anio,
    SUM(i.cantidad) AS total_delitos,
    AVG(i.cantidad) AS promedio_mensual,
    COUNT(*) AS num_registros
FROM incidencia_delictiva i
JOIN estados e ON i.id_estado = e.id_estado
GROUP BY e.nombre, i.anio
ORDER BY i.anio, total_delitos DESC;

-- Vista: Total de delitos por tipo y estado
CREATE VIEW v_delitos_por_tipo_estado AS
SELECT 
    e.nombre AS estado,
    t.categoria AS categoria_delito,
    t.nombre AS tipo_delito,
    SUM(i.cantidad) AS total_delitos,
    AVG(i.cantidad) AS promedio,
    COUNT(*) AS num_registros
FROM incidencia_delictiva i
JOIN estados e ON i.id_estado = e.id_estado
JOIN tipos_delito t ON i.id_tipo_delito = t.id_tipo_delito
GROUP BY e.nombre, t.categoria, t.nombre
ORDER BY total_delitos DESC;

-- Vista: Promedio mensual de delitos
CREATE VIEW v_promedio_mensual AS
SELECT 
    i.mes,
    i.mes_num,
    SUM(i.cantidad) AS total_delitos,
    AVG(i.cantidad) AS promedio_delitos,
    COUNT(*) AS num_registros
FROM incidencia_delictiva i
GROUP BY i.mes, i.mes_num
ORDER BY i.mes_num;

-- Vista: Datos unidos con percepcion
CREATE VIEW v_incidencia_percepcion AS
SELECT 
    e.nombre AS estado,
    i.anio,
    SUM(i.cantidad) AS total_delitos,
    p.percepcion_inseguridad
FROM incidencia_delictiva i
JOIN estados e ON i.id_estado = e.id_estado
LEFT JOIN percepcion_seguridad p ON i.id_estado = p.id_estado AND i.anio = p.anio
GROUP BY e.nombre, i.anio, p.percepcion_inseguridad
ORDER BY i.anio, total_delitos DESC;


-- INSERTAR DATOS INICIALES (CATALOGOS)


-- Insertar estados
INSERT INTO estados (nombre, region) VALUES
('Baja California', 'Noroeste'),
('Sinaloa', 'Noroeste'),
('Chihuahua', 'Norte');


-- PROCEDIMIENTOS ALMACENADOS


DELIMITER //

-- Procedimiento: Obtener estadisticas por estado
CREATE PROCEDURE sp_estadisticas_estado(IN p_estado VARCHAR(100))
BEGIN
    SELECT 
        anio,
        mes,
        categoria_delito,
        SUM(cantidad) AS total_delitos
    FROM v_incidencia_completa
    WHERE estado = p_estado
    GROUP BY anio, mes, categoria_delito
    ORDER BY anio, mes_num;
END //

-- Procedimiento: Obtener top delitos
CREATE PROCEDURE sp_top_delitos(IN p_limite INT)
BEGIN
    SELECT 
        tipo_delito,
        categoria_delito,
        SUM(cantidad) AS total_delitos
    FROM v_incidencia_completa
    GROUP BY tipo_delito, categoria_delito
    ORDER BY total_delitos DESC
    LIMIT p_limite;
END //

DELIMITER ;

-- xxxxx
-- Mostrar resumen de tablas creadas
SHOW TABLES;

-- Mostrar resumen de vistas creadas
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.VIEWS 
WHERE TABLE_SCHEMA = 'seguridad_mexico';
