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

INSERT INTO productos (nombre, descripcion, precio, categoria, imagen_url, disponible, destacado) VALUES
('Espresso Doble', 'Dos shots de espresso corto con un perfil intenso, notas de chocolate amargo y una crema densa.', 2200.0, 'Café', 'https://images.unsplash.com/photo-1510972527409-cef1903972fa?q=80&w=500', 1, 0),

('Flat White', 'Doble shot de espresso con una capa fina de leche vaporizada de textura sedosa. El balance perfecto.', 2800.0, 'Café', 'https://images.unsplash.com/photo-1577968897966-3d4325b36b61?q=80&w=500', 1, 1),

('Capuccino Tradicional', 'Espresso, leche vaporizada y mucha espuma de leche, espolvoreado con cacao fino o canela.', 2700.0, 'Café', 'https://images.unsplash.com/photo-1534778101976-62847782c213?q=80&w=500', 1, 0),

('Iced Latte Vainilla', 'Espresso frío combinado con leche, un toque de jarabe artesanal de vainilla y hielo picado.', 3100.0, 'Bebidas Frías', 'https://images.unsplash.com/photo-1517701604599-bb29b565090c?q=80&w=500', 1, 1),

('Croissant de Almendras', 'Crujiente croissant de masa hojaldrada, relleno y cubierto con crema de almendras tostadas.', 2500.0, 'Pastelería', 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?q=80&w=500', 1, 1),

('Cookie New York con Chips', 'Galleta gigante, súper húmeda por dentro, repleta de trozos de chocolate con leche y semi-amargo.', 1800.0, 'Pastelería', 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?q=80&w=500', 1, 0),

('Cinnamon Roll', 'Rollo de canela tibio, suave y esponjoso, cubierto con un glaseado clásico de queso crema.', 2300.0, 'Pastelería', 'https://images.unsplash.com/photo-1509365465985-25d11c17e812?q=80&w=500', 0, 0),

('Tostado de Jamón y Queso', 'En pan de masa madre casero, con jamón cocido seleccionado y abundante queso dambo derretido.', 3900.0, 'Salado', 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?q=80&w=500', 1, 0),

('Avocado Toast Premium', 'Tostada de masa madre con palta fresca machacada, huevo soft, semillas de sésamo y un hilo de aceite de oliva.', 4500.0, 'Salado', 'https://images.unsplash.com/photo-1603046891744-1f76eb10aec1?q=80&w=500', 1, 1);