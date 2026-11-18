-- Esquema de la base de datos del SIG Alta Facha (SQLite)
-- Basado en el modelo ER normalizado a 3FN

PRAGMA foreign_keys = ON;

CREATE TABLE Proveedor (
    id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL
);

CREATE TABLE Lote (
    id_lote          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_proveedor     INTEGER NOT NULL,
    fecha_recepcion  TEXT NOT NULL,   -- formato AAAA-MM-DD
    costo_total      INTEGER NOT NULL,
    cantidad_prendas INTEGER NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES Proveedor(id_proveedor)
);

CREATE TABLE Prenda (
    id_prenda     INTEGER PRIMARY KEY AUTOINCREMENT,
    id_lote       INTEGER NOT NULL,
    tipo          TEXT NOT NULL,
    talla         TEXT NOT NULL,
    costo         INTEGER NOT NULL,
    precio_venta  INTEGER NOT NULL,
    precio_remate INTEGER,            -- queda NULL hasta que se defina un remate
    estado        TEXT NOT NULL DEFAULT 'disponible'
                  CHECK (estado IN ('disponible', 'en_remate', 'vendida', 'entregada')),
    FOREIGN KEY (id_lote) REFERENCES Lote(id_lote)
);

CREATE TABLE Publicacion (
    id_publicacion    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prenda         INTEGER NOT NULL,
    fecha_publicacion TEXT NOT NULL,
    descripcion       TEXT,
    foto              TEXT,
    FOREIGN KEY (id_prenda) REFERENCES Prenda(id_prenda)
);

CREATE TABLE Cliente (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre     TEXT NOT NULL,
    contacto   TEXT,
    comuna     TEXT
);

CREATE TABLE Distribuidor (
    id_distribuidor INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL
);

CREATE TABLE Pedido (
    id_pedido       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente      INTEGER NOT NULL,
    id_distribuidor INTEGER,          -- NULL si Belén entrega en persona
    fecha_venta     TEXT NOT NULL,
    tipo_entrega    TEXT NOT NULL CHECK (tipo_entrega IN ('propia', 'distribuidor')),
    fecha_entrega   TEXT,             -- NULL mientras no se entregue
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (id_distribuidor) REFERENCES Distribuidor(id_distribuidor)
);

CREATE TABLE DetallePedido (
    id_pedido    INTEGER NOT NULL,
    id_prenda    INTEGER NOT NULL UNIQUE,  -- cada prenda se vende una sola vez
    precio_final INTEGER NOT NULL,
    margen       INTEGER NOT NULL,         -- precio_final - costo
    PRIMARY KEY (id_pedido, id_prenda),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido),
    FOREIGN KEY (id_prenda) REFERENCES Prenda(id_prenda)
);

CREATE TABLE AlertaRemate (
    id_alerta      INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prenda      INTEGER NOT NULL,
    fecha_alerta   TEXT NOT NULL,
    dias_sin_venta INTEGER NOT NULL,
    margen_remate  REAL,              -- lo define Belén al atender la alerta (ej: 1.0 = 100% sobre el costo)
    estado_alerta  TEXT NOT NULL DEFAULT 'pendiente'
                   CHECK (estado_alerta IN ('pendiente', 'atendida')),
    FOREIGN KEY (id_prenda) REFERENCES Prenda(id_prenda)
);

-- Parametros que Belén ingresa desde la aplicacion (una sola fila)
CREATE TABLE Configuracion (
    id_config   INTEGER PRIMARY KEY CHECK (id_config = 1),
    umbral_dias INTEGER NOT NULL
);
