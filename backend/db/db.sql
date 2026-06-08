CREATE DATABASE IF NOT EXISTS cafeteria;
use cafeteria;

CREATE TABLE usuarios(
    id_usuario INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'user') DEFAULT 'user',
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_token_expiration DATETIME DEFAULT NULL
);
CREATE TABLE locales(
    id_local INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL DEFAULT "Cafeteria 11",
    pais VARCHAR(150) NOT NULL DEFAULT "Argentina",
    provincia VARCHAR(150) NOT NULL DEFAULT "Buenos Aires",
    direccion VARCHAR(255) NOT NULL DEFAULT "Av. Paseo Colon 860",
    horario_apertura TIME NOT NULL DEFAULT '08:00:00',
    horario_cierre TIME NOT NULL DEFAULT '23:00:00'
);
CREATE TABLE productos(
    id_producto INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    precio DECIMAL(6,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    tipo VARCHAR(150),
    local_producto INT NOT NULL,
    FOREIGN KEY(local_producto) REFERENCES locales(id_local)
);
CREATE TABLE  resenas(
    id_resena INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_producto INT NOT NULL,
    puntuacion INT NOT NULL CHECK (puntuacion >= 1 AND puntuacion <= 5),
    comentario TEXT,
    fecha_resena TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(id_producto) REFERENCES productos(id_producto)
);
CREATE TABLE reservas (
    id_reserva INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    usuario_reserva INT NULL,
    producto_reserva INT NULL,
    nombre_cliente VARCHAR(100) NOT NULL,
    correo_cliente VARCHAR(120) NOT NULL,
    tipo_reserva ENUM('mesa', 'producto') NOT NULL,
    fecha_reserva DATE NOT NULL,
    hora_reserva TIME NOT NULL,
    numero_personas INT NULL,
    comentarios TEXT,
    estado VARCHAR(50) NOT NULL DEFAULT 'En proceso',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_reserva) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (producto_reserva) REFERENCES productos(id_producto)
);
CREATE TABLE historial_acciones (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    accion VARCHAR(255) NOT NULL,
    tipo ENUM('reserva', 'venta', 'producto', 'usuario') NOT NULL,
    detalle TEXT,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);