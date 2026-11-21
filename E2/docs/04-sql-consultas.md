# Consultas SQL de negocio e interpretación

> Las rutas son relativas a `E2/app/`. Las consultas están en `sql/consultas.sql` (consultas 1 a 3) y `sql/kpi_consultas_propuestas.sql` (KPI). Se ejecutan con `python probar_consultas.py` sobre la base creada por `python crear_bd.py`.

**Datos de prueba ficticios:** las cifras de este documento salen de `sql/datos_prueba.sql` y no son resultados reales de Alta Facha. Las fechas de prueba son relativas al día en que se crea la base, de modo que los resultados de las consultas 1, 2c y 3 son los mismos cualquier día. Solo cambia el reparto por mes de la consulta 2b.

## Cómo está construido el SQL

- **Esquema (`sql/schema.sql`):** 10 tablas en 3FN con 10 claves primarias (una compuesta), 8 claves foráneas, 4 restricciones CHECK y 1 UNIQUE. Activa `PRAGMA foreign_keys = ON`.
- **Datos de prueba (`sql/datos_prueba.sql`):** 2 proveedores, 3 lotes, 26 prendas, 26 publicaciones, 4 clientas, 2 distribuidores, 7 pedidos con 12 prendas vendidas, 1 alerta atendida y umbral inicial de 30 días.
- **Fechas:** `julianday('now', 'localtime')` para contar días con la hora de Chile (con `'now'` solo, SQLite usa hora UTC y después de las 21:00 el día ya cambia).

## Consulta 1. Stock y su antigüedad

**Pregunta:** ¿qué prendas se pueden vender hoy y cuánto tiempo llevan en stock?

```sql
SELECT p.id_prenda, p.tipo, p.talla, p.precio_venta, p.precio_remate, p.estado,
       CAST(julianday('now', 'localtime') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_en_stock
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote
WHERE p.estado IN ('disponible', 'en_remate')
ORDER BY dias_en_stock DESC;
```

**Interpretación.** Hay 14 prendas en stock (stock = disponibles + en remate): 13 disponibles y 1 en remate (la prenda 10, a 6.000 en vez de 12.000). Las más antiguas, del lote 1, llevan 60 días; las del lote 2, 35 días y las del lote 3, 10 días. Antes Belén solo podía saber esto revisando su catálogo a mano.

**Consulta 1b (stock por tipo).** `GROUP BY tipo` sobre las mismas prendas: blusa 5, falda 3, abrigo 2, chaqueta 2 y vestido 2. Las blusas son 5 de las 14 prendas (35,7 %).

**Consulta 1c (inventario por estado, K1).** `GROUP BY estado` sobre todas las prendas: disponible 13, en remate 1, vendida 4 y entregada 8 (26 en total).

## Consulta 2. Ventas y margen por prenda vendida

**Pregunta:** ¿cuánto se ganó en cada prenda vendida?

```sql
SELECT pe.id_pedido, pe.fecha_venta, c.nombre AS clienta, p.id_prenda, p.tipo,
       p.costo, d.precio_final, d.margen
FROM DetallePedido d
JOIN Pedido pe ON d.id_pedido = pe.id_pedido
JOIN Prenda p ON d.id_prenda = p.id_prenda
JOIN Cliente c ON pe.id_cliente = c.id_cliente
ORDER BY pe.fecha_venta;
```

**Interpretación.** Se vendieron 12 prendas en 7 pedidos. El margen por prenda va de 9.000 (blusa y falda a 12.000) a 14.500 (abrigo y chaqueta a 18.000), con un margen medio de unos 12.083 por prenda. Es el cálculo que hoy se hace a mano en el Excel y que ahora queda guardado en cada venta (`DetallePedido.margen`).

## Consulta 2b. Ventas y margen por mes (K2)

```sql
SELECT strftime('%Y-%m', pe.fecha_venta) AS mes,
       COUNT(*) AS prendas_vendidas,
       SUM(d.precio_final) AS ventas,
       SUM(d.margen) AS margen
FROM DetallePedido d
JOIN Pedido pe ON d.id_pedido = pe.id_pedido
GROUP BY mes
ORDER BY mes;
```

**Interpretación.** En total, 183.000 CLP en ventas y 145.000 CLP de margen. El reparto por mes depende del día en que se crea la base; los totales no.

## Consulta 2c. Ventas y margen por lote (K4)

**Pregunta:** ¿cuánto se ha recuperado de cada inversión? Belén fija el precio para duplicar lo invertido en cada lote (respuesta 2 del cuestionario), por lo que `veces_inversion` se compara con la meta de 2,0.

```sql
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
```

| Lote | Costo total | Prendas vendidas | Ventas | Veces la inversión |
|---|---|---|---|---|
| 1 | 30.000 | 6 de 10 | 85.000 | 2,83 |
| 2 | 28.000 | 4 de 8 | 68.000 | 2,43 |
| 3 | 24.000 | 2 de 8 | 30.000 | 1,25 |

**Interpretación.** Los lotes 1 y 2 ya superaron la meta de duplicar lo invertido y aún tienen prendas en stock. El lote 3, recibido hace 10 días, lleva 1,25 veces. La comparación entre lotes ayuda a decidir a qué proveedor volver a comprar. El `LEFT JOIN` mantiene en el resultado los lotes sin ventas.

## Consulta 3. Prendas sobre el umbral de días sin venta (K5)

**Pregunta:** ¿qué prendas conviene rematar? Es la misma condición que usa `alerta_remate.py`.

```sql
SELECT p.id_prenda, p.tipo, p.talla, l.fecha_recepcion,
       CAST(julianday('now', 'localtime') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_sin_venta,
       c.umbral_dias
FROM Prenda p
JOIN Lote l ON p.id_lote = l.id_lote
JOIN Configuracion c ON c.id_config = 1
WHERE p.estado = 'disponible'
  AND julianday('now', 'localtime') - julianday(l.fecha_recepcion) > c.umbral_dias
ORDER BY dias_sin_venta DESC;
```

**Interpretación.** Con umbral 30, 7 de las 13 prendas disponibles (53,8 %) superan el umbral: tres con 60 días (ids 7, 8 y 9) y cuatro con 35 (ids 15, 16, 17 y 18). La prenda 10 no aparece porque ya está en remate. Con umbral 50 solo quedan 3 (23,1 %).

## Consultas de los KPI que no están en `consultas.sql`

**K3, margen bruto porcentual y margen medio por prenda:**

```sql
SELECT SUM(precio_final) AS ventas,
       SUM(margen)       AS margen,
       ROUND(100.0 * SUM(margen) / SUM(precio_final), 1) AS margen_pct,
       COUNT(*)          AS prendas_vendidas,
       ROUND(1.0 * SUM(margen) / COUNT(*), 0) AS margen_medio_prenda
FROM DetallePedido;
```

Resultado: ventas 183.000, margen 145.000, margen 79,2 % y margen medio 12.083 por prenda.

**K4 ampliado** (resultado neto = ventas − costo del lote, y % vendido): lotes 1, 2 y 3 con resultado neto 55.000, 40.000 y 6.000, y 60 %, 50 % y 25 % vendido.

**K5, porcentaje del stock disponible sobre el umbral:** `SUM(CASE ... THEN 1 ELSE 0 END) / COUNT(*)` sobre las prendas disponibles, con el mismo criterio de la consulta 3.

## Valores de verificación

| Consulta | Resultado esperado con la base recién creada y umbral 30 |
|---|---|
| 1 | 14 prendas en stock (13 disponibles + 1 en remate) |
| 1c | disponible 13, en remate 1, vendida 4, entregada 8 |
| 2 | 12 prendas vendidas en 7 pedidos |
| 2b | ventas 183.000 y margen 145.000 |
| 2c | 2,83 / 2,43 / 1,25 veces la inversión |
| 3 | 7 prendas (ids 7, 8, 9, 15, 16, 17 y 18) |

Estos valores se comprueban automáticamente en `tests/test_kpis.py` y `tests/test_funciones_bd.py`.
