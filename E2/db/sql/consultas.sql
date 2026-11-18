-- 1. Stock disponible (prendas que todavia se pueden vender)
SELECT p.id_prenda, p.tipo, p.talla, p.precio_venta, p.precio_remate, p.estado,
       CAST(julianday('now') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_en_stock
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote
WHERE p.estado IN ('disponible', 'en_remate')
ORDER BY dias_en_stock DESC;

-- 1b. Stock disponible por tipo de prenda
SELECT tipo, COUNT(*) AS cantidad
FROM Prenda
WHERE estado IN ('disponible', 'en_remate')
GROUP BY tipo
ORDER BY cantidad DESC;

-- 2. Ventas y margen por prenda vendida
SELECT pe.id_pedido, pe.fecha_venta, c.nombre AS clienta, p.id_prenda, p.tipo,
       p.costo, d.precio_final, d.margen
FROM DetallePedido d
JOIN Pedido pe ON d.id_pedido = pe.id_pedido
JOIN Prenda p ON d.id_prenda = p.id_prenda
JOIN Cliente c ON pe.id_cliente = c.id_cliente
ORDER BY pe.fecha_venta;

-- 2b. Ventas y margen por mes
SELECT strftime('%Y-%m', pe.fecha_venta) AS mes,
       COUNT(*) AS prendas_vendidas,
       SUM(d.precio_final) AS ventas,
       SUM(d.margen) AS margen
FROM DetallePedido d
JOIN Pedido pe ON d.id_pedido = pe.id_pedido
GROUP BY mes
ORDER BY mes;

-- 2c. Ventas y margen por lote (incluye cuanto se ha recuperado de la inversion)
SELECT l.id_lote, l.fecha_recepcion, l.costo_total, l.cantidad_prendas,
       COUNT(d.id_prenda) AS prendas_vendidas,
       COALESCE(SUM(d.precio_final), 0) AS ventas,
       COALESCE(SUM(d.margen), 0) AS margen_prendas_vendidas,
       ROUND(COALESCE(SUM(d.precio_final), 0) * 1.0 / l.costo_total, 2) AS veces_inversion
FROM Lote l
JOIN Prenda p ON p.id_lote = l.id_lote
LEFT JOIN DetallePedido d ON d.id_prenda = p.id_prenda
GROUP BY l.id_lote
ORDER BY l.id_lote;

-- 3. Prendas que superan el umbral de dias sin venta (umbral ingresado por Belén)
SELECT p.id_prenda, p.tipo, p.talla, l.fecha_recepcion,
       CAST(julianday('now') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_sin_venta,
       c.umbral_dias
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote
JOIN Configuracion c ON c.id_config = 1
WHERE p.estado = 'disponible'
  AND julianday('now') - julianday(l.fecha_recepcion) > c.umbral_dias
ORDER BY dias_sin_venta DESC;
