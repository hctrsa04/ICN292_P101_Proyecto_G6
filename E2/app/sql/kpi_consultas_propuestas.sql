-- =====================================================================
-- SIG Alta Facha - Consultas de KPI propuestas (borrador para revisar)
-- Probadas contra la base de prueba generada por crear_bd.py.
-- Cada KPI indica: formula, fuente (tablas) y estado (EXISTE = ya esta en
-- consultas.sql / NUEVA = propuesta).
-- Nota de fechas: se usa 'localtime' porque 'now' en SQLite es hora UTC y
-- en Chile despues de las ~21:00 ya cuenta como el dia siguiente.
-- Estado de la revision: K1 ya fue incorporado a consultas.sql (consulta 1c) y
-- a funciones_bd.py (inventario_por_estado) en AltaFacha_SIG_corregido.
-- El resto (K3 y K4 ampliado) son PROPUESTAS pendientes de aprobacion del equipo.
-- K6 a K9 se retiraron el 21-nov porque no estan en el informe E2.
-- =====================================================================

-- K1 (INCORPORADO en consultas.sql 1c) Inventario por estado (RF-09)
-- Formula: COUNT(prendas) agrupado por estado.  Fuente: Prenda.estado
SELECT estado, COUNT(*) AS prendas
FROM Prenda
GROUP BY estado
ORDER BY CASE estado WHEN 'disponible' THEN 1 WHEN 'en_remate' THEN 2
                     WHEN 'vendida' THEN 3 ELSE 4 END;

-- K2 (EXISTE: 2b) Ventas y margen bruto por mes
-- Formula: SUM(precio_final), SUM(margen) por mes de fecha_venta.
-- Fuente: DetallePedido, Pedido.fecha_venta   (ver consultas.sql, 2b)

-- K3 (NUEVA) Margen bruto porcentual y margen medio por prenda
-- Formula: SUM(margen) / SUM(precio_final) * 100, y SUM(margen) / prendas vendidas.
-- Fuente: DetallePedido. Base de prueba: 79,2 % y 12.083 (coincide con el informe E2).
SELECT SUM(precio_final) AS ventas,
       SUM(margen)       AS margen,
       ROUND(100.0 * SUM(margen) / SUM(precio_final), 1) AS margen_pct,
       COUNT(*)          AS prendas_vendidas,
       ROUND(1.0 * SUM(margen) / COUNT(*), 0) AS margen_medio_prenda
FROM DetallePedido;

-- K4 (EXISTE parcial: 2c) Recuperacion de la inversion por lote
-- META de Belen (respuesta 2 del cuestionario, informe E2 seccion 5.2): veces_inversion >= 2,0.
-- Base de prueba: 2,83 / 2,43 / 1,25.
-- 2c ya entrega ventas, margen de prendas vendidas y veces_inversion.
-- Se agrega el resultado neto (ventas - costo_total del lote) y el % vendido,
-- porque el "margen de prendas vendidas" ignora el costo de las no vendidas.
SELECT l.id_lote, l.fecha_recepcion, l.costo_total,
       COUNT(d.id_prenda) AS vendidas, l.cantidad_prendas,
       ROUND(100.0 * COUNT(d.id_prenda) / l.cantidad_prendas, 1) AS pct_vendido,
       COALESCE(SUM(d.precio_final), 0) AS ventas,
       COALESCE(SUM(d.precio_final), 0) - l.costo_total AS resultado_neto,
       ROUND(COALESCE(SUM(d.precio_final), 0) * 1.0 / l.costo_total, 2) AS veces_inversion
FROM Lote l
JOIN Prenda p ON p.id_lote = l.id_lote
LEFT JOIN DetallePedido d ON d.id_prenda = p.id_prenda
GROUP BY l.id_lote
ORDER BY l.id_lote;

-- K5 (EXISTE: 3) Prendas sobre el umbral de dias sin venta
-- Se agrega el % del stock disponible que esta sobre el umbral.
-- Formula: prendas 'disponible' con dias > umbral / prendas 'disponible'.
-- Base de prueba: umbral 30 da 7 de 13 (53,8 %), umbral 50 da 3 de 13 (23,1 %), como el informe E2.
-- (misma regla que alerta_remate.py, ver pendiente 7 del informe sobre el borde "> umbral")
SELECT SUM(CASE WHEN julianday('now','localtime') - julianday(l.fecha_recepcion) > c.umbral_dias
                THEN 1 ELSE 0 END) AS sobre_umbral,
       COUNT(*) AS disponibles,
       ROUND(100.0 * SUM(CASE WHEN julianday('now','localtime') - julianday(l.fecha_recepcion) > c.umbral_dias
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_sobre_umbral
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote
JOIN Configuracion c ON c.id_config = 1
WHERE p.estado = 'disponible';
