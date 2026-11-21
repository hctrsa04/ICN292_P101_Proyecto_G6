# KPI del SIG Alta Facha (K1 a K5), solo lectura.
# Cada funcion devuelve un DataFrame de pandas. Las consultas son las de
# sql/consultas.sql y sql/kpi_consultas_propuestas.sql (con 'localtime'), sin cambios
# de calculo. Definicion y metas: ../docs/05-kpi-dashboard.md.
# Se usa funciones_bd.conectar() para leer la misma base que la app (y la temporal en tests).

import pandas as pd

import funciones_bd

# Unica meta definida hoy (K4): duplicar lo invertido en cada lote.
# Origen: Belen, respuesta 2 del cuestionario; informe E2, secciones 1.3 y 5.2.
META_K4 = 2.0

ESTADOS = ["disponible", "en_remate", "vendida", "entregada"]


def leer(sql):
    con = funciones_bd.conectar()
    try:
        return pd.read_sql_query(sql, con)
    finally:
        con.close()


def k1_inventario_por_estado():
    """K1 - Inventario por estado.

    Formula: conteo de prendas agrupado por estado.
    Fuente: Prenda.estado. Consulta: consultas.sql 1c.
    Meta: por definir con Belen.
    Devuelve columnas estado, prendas (los 4 estados en orden, con 0 si no hay prendas).
    """
    tabla = leer("""
        SELECT estado, COUNT(*) AS prendas
        FROM Prenda
        GROUP BY estado
        ORDER BY CASE estado WHEN 'disponible' THEN 1 WHEN 'en_remate' THEN 2
                             WHEN 'vendida' THEN 3 ELSE 4 END
    """)
    # GROUP BY omite los estados sin prendas: se agregan con 0 para que siempre esten los 4
    tabla = tabla.set_index("estado").reindex(ESTADOS, fill_value=0).reset_index()
    return tabla


def k2_ventas_margen_mensual():
    """K2 - Ventas y margen bruto mensual.

    Formula: SUM(precio_final) y SUM(margen) por mes de fecha_venta.
    Fuente: DetallePedido.precio_final, DetallePedido.margen, Pedido.fecha_venta.
    Consulta: consultas.sql 2b.
    Meta: por definir con Belen.
    Devuelve columnas mes (AAAA-MM), prendas_vendidas, ventas, margen.
    """
    return leer("""
        SELECT strftime('%Y-%m', pe.fecha_venta) AS mes,
               COUNT(*) AS prendas_vendidas,
               SUM(d.precio_final) AS ventas,
               SUM(d.margen) AS margen
        FROM DetallePedido d
        JOIN Pedido pe ON d.id_pedido = pe.id_pedido
        GROUP BY mes
        ORDER BY mes
    """)


def k3_margen_bruto():
    """K3 - Margen bruto porcentual y margen medio por prenda.

    Formula: SUM(margen) / SUM(precio_final) * 100; complemento: SUM(margen) / prendas vendidas.
    Margen bruto = precio_final - costo individual de la prenda (no resta despacho).
    Fuente: DetallePedido.precio_final, DetallePedido.margen.
    Consulta: kpi_consultas_propuestas.sql K3.
    Meta: por definir con Belen.
    Devuelve una fila: ventas, margen, margen_pct, prendas_vendidas, margen_medio_prenda
    (sin ventas, los valores vienen vacios / NULL).
    """
    # TODO(Belén): ¿el margen debe incluir el despacho? Hoy es margen bruto (punto abierto 3).
    return leer("""
        SELECT SUM(precio_final) AS ventas,
               SUM(margen)       AS margen,
               ROUND(100.0 * SUM(margen) / SUM(precio_final), 1) AS margen_pct,
               COUNT(*)          AS prendas_vendidas,
               ROUND(1.0 * SUM(margen) / COUNT(*), 0) AS margen_medio_prenda
        FROM DetallePedido
    """)


def k4_recuperacion_por_lote():
    """K4 - Recuperacion de la inversion por lote.

    Formula: veces_inversion = ventas / Lote.costo_total.
    Complementos: resultado_neto = ventas - costo_total; pct_vendido = vendidas / cantidad_prendas * 100.
    Fuente: Lote (costo_total, cantidad_prendas, fecha_recepcion), Prenda.id_lote,
    DetallePedido.precio_final. Consulta: consultas.sql 2c ampliada (kpi_consultas_propuestas.sql K4).
    Meta: >= 2,0 veces la inversion (META_K4), segun Belen (informe E2).
    Devuelve una fila por lote: id_lote, fecha_recepcion, costo_total, vendidas,
    cantidad_prendas, pct_vendido, ventas, resultado_neto, veces_inversion.
    """
    return leer("""
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
        ORDER BY l.id_lote
    """)


def k5_stock_sobre_umbral():
    """K5 - % del stock disponible sobre el umbral de dias sin venta.

    Formula: prendas 'disponible' con dias > umbral / prendas 'disponible' * 100.
    Dias = hoy (hora de Chile) - Lote.fecha_recepcion, misma regla que alerta_remate.py.
    Fuente: Prenda.estado, Lote.fecha_recepcion, Configuracion.umbral_dias.
    Consulta: consultas.sql 3 y kpi_consultas_propuestas.sql K5.
    Meta: por definir con Belen.
    Devuelve una fila: sobre_umbral, disponibles, pct_sobre_umbral, umbral_dias
    (umbral_dias se agrega para mostrar con que umbral se calculo).
    """
    # TODO(Belén): dias desde la llegada del lote o desde la publicacion (P3);
    #              borde del umbral, dia 30 o 31 (P4).
    return leer("""
        SELECT SUM(CASE WHEN julianday('now','localtime') - julianday(l.fecha_recepcion) > c.umbral_dias
                        THEN 1 ELSE 0 END) AS sobre_umbral,
               COUNT(*) AS disponibles,
               ROUND(100.0 * SUM(CASE WHEN julianday('now','localtime') - julianday(l.fecha_recepcion) > c.umbral_dias
                                      THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_sobre_umbral,
               (SELECT umbral_dias FROM Configuracion WHERE id_config = 1) AS umbral_dias
        FROM Prenda p
        JOIN Lote l ON p.id_lote = l.id_lote
        JOIN Configuracion c ON c.id_config = 1
        WHERE p.estado = 'disponible'
    """)
