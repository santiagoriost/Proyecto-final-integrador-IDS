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
    descripcion VARCHAR(255) NULL,
    imagen VARCHAR(255) NULL,
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
CREATE TABLE ventas (
    id_venta INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalle_ventas (
    id_detalle INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(6,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (venta_id) REFERENCES ventas(id_venta),
    FOREIGN KEY (producto_id) REFERENCES productos(id_producto)
);

CREATE TABLE carritos (
    id_carrito INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL UNIQUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario)
);

CREATE TABLE carrito_items (
    id_item INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_carrito) REFERENCES carritos(id_carrito) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),

    UNIQUE(id_carrito, id_producto)
);

INSERT INTO locales (nombre, pais, provincia, direccion, horario_apertura, horario_cierre)
VALUES ('Cafeteria Sede Central', 'Argentina', 'Buenos Aires', 'Av. Paseo Colon 860', '08:00:00', '23:00:00');

INSERT INTO productos (nombre, precio, stock, tipo, local_producto, descripcion) VALUES
-- Cafes calientes
('Cafe Espresso', 1800.00, 50, 'Cafe', 1, 'Espresso clasico e intenso con granos seleccionados.'),
('Cafe Doble', 2300.00, 50, 'Cafe', 1, 'Doble carga de espresso para arrancar el dia con todo.'),
('Americano', 2000.00, 40, 'Cafe', 1, 'Espresso estirado con agua caliente, suave y aromatico.'),
('Cafe Latte', 2500.00, 60, 'Cafe', 1, 'Espresso con leche al vapor y una fina capa de espuma.'),
('Capuccino', 2700.00, 45, 'Cafe', 1, 'Espresso, leche y mucha espuma, espolvoreado con cacao.'),
('Flat White', 2800.00, 35, 'Cafe', 1, 'Doble shot de espresso con leche texturizada sutilmente.'),
('Submarino', 2600.00, 20, 'Bebida Caliente', 1, 'Leche caliente servida con una barra de chocolate para derretir.'),

-- Cafes Frios & Bebidas Frias
('Iced Latte', 2700.00, 30, 'Cafe Frio', 1, 'Nuestro clasico Latte servido con hielo y muy refrescante.'),
('Frappuccino de Caramelo', 3200.00, 25, 'Cafe Frio', 1, 'Cafe licuado con hielo, leche, salsa de caramelo y crema batida.'),
('Licuado de Banana', 2400.00, 15, 'Bebida Fria', 1, 'Licuado tradicional con leche y bananas frescas.'),
('Exprimido de Naranja', 2500.00, 30, 'Bebida Fria', 1, 'Jugo de naranja 100% natural y exprimido en el momento.'),

-- Pasteleria Dulce
('Medialuna de Grasa', 600.00, 100, 'Dulce', 1, 'Clasica medialuna argentina de grasa, crocante y saladita.'),
('Medialuna de Manteca', 600.00, 100, 'Dulce', 1, 'Medialuna de manteca super esponjosa con almibar.'),
('Croissant', 1400.00, 40, 'Dulce', 1, 'Estilo frances, hojaldrado y dorado a la perfeccion.'),
('Alfajor de Almendra', 1800.00, 30, 'Dulce', 1, 'Alfajor de masa de almendras relleno de mucho dulce de leche.'),
('Cookie con Chips', 1100.00, 45, 'Dulce', 1, 'Galleta casera con pedazos de chocolate semi-amargo.'),
('Brownie con Nuez', 1900.00, 20, 'Dulce', 1, 'Humedo por dentro, con nueces crocantes y mucho chocolate.'),
('Porcion de Lemon Pie', 2900.00, 12, 'Dulce', 1, 'Base de masa dulce, crema de limon y merengue italiano dorado.'),
('Porcion de Cheesecake', 3200.00, 10, 'Dulce', 1, 'Tarta de queso crema con salsa artesanal de frutos rojos.'),

-- Salados
('Tostado de Jamon y Queso', 3500.00, 25, 'Salado', 1, 'Tostado en pan de miga con jamon cocido y queso tybo derretido.'),
('Avocado Toast', 4200.00, 15, 'Salado', 1, 'Toston de pan de masa madre con palta pisada, huevo poche y semillas.'),
('Chipa Porcion', 1200.00, 60, 'Salado', 1, 'Porcion de 4 pancitos de queso calientes y libres de gluten.'),
('Sandwich de Lomito y Queso', 4800.00, 15, 'Salado', 1, 'En pan ciabatta con lomito ahumado, queso, rucula y tomate.'),

-- Te
('Te Hebras Earl Grey', 1800.00, 40, 'Te', 1, 'Te negro aromatizado con aceite de bergamota.'),
('Te Verde con Jazmin', 1800.00, 35, 'Te', 1, 'Te verde delicado y floral, ideal para relajar.');