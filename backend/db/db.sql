CREATE DATABASE IF NOT EXISTS cafeteria;
use cafeteria;
CREATE TABLE usuarios(
    id_usuario INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    clave VARCHAR(100) NOT NULL
);
CREATE TABLE administradores(
    id_admin INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    clave VARCHAR(150) NOT NULL
);
CREATE TABLE locales(
    id_local INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL DEFAULT "Cafeteria 11",
    pais VARCHAR(150) NOT NULL DEFAULT "Argentina",
    provincia VARCHAR(150) NOT NULL DEFAULT "Buenos Aires",
    direccion VARCHAR(255) NOT NULL
);
CREATE TABLE productos(
    id_producto INT NOT NULL PRIMARY KEY AUTO_INCREMENT.
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(6,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    tipo VARCHAR(150),
    local_producto INT NOT NULL,
    FOREIGN KEY(local_producto) REFERENCES locales(id_local)
);
CREATE TABLE reservas(
    id_reserva INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    usuario_reserva INT NOT NULL,
    producto_reserva INT NOT NULL,
    fecha_reserva TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TIMESTAMP,
    estado VARCHAR(50) NOT NULL DEFAULT "En proceso",
    FOREIGN KEY(usuario_reserva) REFERENCES usuarios(id_usuario),
    FOREIGN KEY(producto_reserva) REFERENCES productos(id_producto)
)