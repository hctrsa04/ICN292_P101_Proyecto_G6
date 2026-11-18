-- Datos de prueba (ficticios)
-- Las fechas son relativas al dia en que se crea la base, asi las pruebas
-- dan el mismo resultado sin importar cuando se ejecuten.

INSERT INTO Configuracion (id_config, umbral_dias) VALUES (1, 30);

INSERT INTO Proveedor (nombre) VALUES
('Mayorista Fardos A'),
('Mayorista Fardos B');

INSERT INTO Lote (id_proveedor, fecha_recepcion, costo_total, cantidad_prendas) VALUES
(1, date('now', '-60 days'), 30000, 10),
(2, date('now', '-35 days'), 28000, 8),
(1, date('now', '-10 days'), 24000, 8);

INSERT INTO Prenda (id_lote, tipo, talla, costo, precio_venta, precio_remate, estado) VALUES
-- lote 1
(1, 'vestido',  'M', 3000, 15000, NULL, 'entregada'),
(1, 'vestido',  'L', 3000, 15000, NULL, 'entregada'),
(1, 'blusa',    'S', 3000, 12000, NULL, 'entregada'),
(1, 'abrigo',   'M', 3000, 18000, NULL, 'entregada'),
(1, 'vestido',  'S', 3000, 15000, NULL, 'entregada'),
(1, 'falda',    'M', 3000, 12000, NULL, 'vendida'),
(1, 'blusa',    'M', 3000, 12000, NULL, 'disponible'),
(1, 'vestido',  'L', 3000, 15000, NULL, 'disponible'),
(1, 'falda',    'S', 3000, 12000, NULL, 'disponible'),
(1, 'blusa',    'L', 3000, 12000, 6000, 'en_remate'),
-- lote 2
(2, 'abrigo',   'L', 3500, 18000, NULL, 'entregada'),
(2, 'chaqueta', 'M', 3500, 18000, NULL, 'entregada'),
(2, 'vestido',  'M', 3500, 16000, NULL, 'entregada'),
(2, 'vestido',  'S', 3500, 16000, NULL, 'vendida'),
(2, 'abrigo',   'M', 3500, 18000, NULL, 'disponible'),
(2, 'chaqueta', 'L', 3500, 18000, NULL, 'disponible'),
(2, 'blusa',    'M', 3500, 13000, NULL, 'disponible'),
(2, 'falda',    'L', 3500, 13000, NULL, 'disponible'),
-- lote 3
(3, 'vestido',  'M', 3000, 15000, NULL, 'vendida'),
(3, 'vestido',  'L', 3000, 15000, NULL, 'vendida'),
(3, 'blusa',    'S', 3000, 12000, NULL, 'disponible'),
(3, 'blusa',    'M', 3000, 12000, NULL, 'disponible'),
(3, 'falda',    'M', 3000, 12000, NULL, 'disponible'),
(3, 'vestido',  'S', 3000, 15000, NULL, 'disponible'),
(3, 'chaqueta', 'L', 3000, 17000, NULL, 'disponible'),
(3, 'abrigo',   'M', 3000, 18000, NULL, 'disponible');

-- una publicacion por prenda, 3 dias despues de recibir el lote
INSERT INTO Publicacion (id_prenda, fecha_publicacion, descripcion, foto)
SELECT p.id_prenda, date(l.fecha_recepcion, '+3 days'), p.tipo || ' talla ' || p.talla, NULL
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote;

INSERT INTO Cliente (nombre, contacto, comuna) VALUES
('Clienta Prueba 1', '@clienta1', 'Las Condes'),
('Clienta Prueba 2', '@clienta2', 'Maipu'),
('Clienta Prueba 3', '@clienta3', 'Vitacura'),
('Clienta Prueba 4', '@clienta4', 'La Florida');

INSERT INTO Distribuidor (nombre) VALUES
('Agencia de delivery 1'),
('Agencia de delivery 2');

INSERT INTO Pedido (id_cliente, id_distribuidor, fecha_venta, tipo_entrega, fecha_entrega) VALUES
(1, NULL, date('now', '-55 days'), 'propia',       date('now', '-54 days')),
(2, 1,    date('now', '-50 days'), 'distribuidor', date('now', '-48 days')),
(3, NULL, date('now', '-45 days'), 'propia',       date('now', '-45 days')),
(1, 1,    date('now', '-30 days'), 'distribuidor', date('now', '-28 days')),
(4, 2,    date('now', '-20 days'), 'distribuidor', date('now', '-18 days')),
(2, NULL, date('now', '-5 days'),  'propia',       NULL),
(3, 2,    date('now', '-3 days'),  'distribuidor', NULL);

-- margen = precio_final - costo de la prenda
INSERT INTO DetallePedido (id_pedido, id_prenda, precio_final, margen) VALUES
(1, 1,  15000, 12000),
(1, 2,  15000, 12000),
(2, 3,  12000,  9000),
(3, 4,  16000, 13000),
(4, 5,  15000, 12000),
(4, 11, 18000, 14500),
(5, 12, 18000, 14500),
(5, 13, 16000, 12500),
(6, 6,  12000,  9000),
(6, 14, 16000, 12500),
(7, 19, 15000, 12000),
(7, 20, 15000, 12000);

-- la prenda 10 ya paso por una alerta que Belén atendio (margen 100% sobre el costo)
INSERT INTO AlertaRemate (id_prenda, fecha_alerta, dias_sin_venta, margen_remate, estado_alerta) VALUES
(10, date('now', '-25 days'), 35, 1.0, 'atendida');
