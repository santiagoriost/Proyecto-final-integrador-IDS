CREATE DATABASE IF NOT EXISTS cafeteria;
use cafeteria;
CREATE TABLE roles(
    id_rol INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre_rol VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE cuentas(
    id_cuenta INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL,
    rol INT NOT NULL,
    FOREIGN KEY(rol) REFERENCES roles(id_rol)
);
CREATE TABLE locales(
    id_local INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL DEFAULT "Cafeteria 11",
    pais VARCHAR(150) NOT NULL DEFAULT "Argentina",
    provincia VARCHAR(150) NOT NULL DEFAULT "Buenos Aires",
    direccion VARCHAR(255) NOT NULL DEFAULT "Av. Paseo Colon 860"
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
CREATE TABLE reservas(
    id_reserva INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    usuario_reserva INT NOT NULL,
    producto_reserva INT NOT NULL,
    fecha_reserva TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega TIMESTAMP,
    estado VARCHAR(50) NOT NULL DEFAULT "En proceso",
    FOREIGN KEY(usuario_reserva) REFERENCES cuentas(id_cuenta),
    FOREIGN KEY(producto_reserva) REFERENCES productos(id_producto)
);