"""Pruebas base de funciones_bd.py (unittest, biblioteca estandar).

Cada prueba crea una base temporal con schema.sql + datos_prueba.sql, asi nunca
toca data/altafacha.db. Ejecutar desde la carpeta raiz del proyecto:

    python -m unittest discover -s tests -v
"""
import os
import sqlite3
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import funciones_bd as f  # noqa: E402


def crear_base_temporal(ruta):
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON")
    for archivo in ("schema.sql", "datos_prueba.sql"):
        with open(os.path.join(RAIZ, "sql", archivo), encoding="utf-8") as fh:
            con.executescript(fh.read())
    con.commit()
    con.close()


class PruebaBase(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "prueba.db")
        crear_base_temporal(self.ruta)
        self.ruta_original = f.ruta_bd
        f.ruta_bd = self.ruta  # las funciones usan esta variable global

    def tearDown(self):
        f.ruta_bd = self.ruta_original
        self.carpeta.cleanup()

    def contar(self, sql, params=()):
        con = sqlite3.connect(self.ruta)
        try:
            return con.execute(sql, params).fetchone()[0]
        finally:
            con.close()


class PruebasInventario(PruebaBase):
    def test_inventario_por_estado_datos_de_prueba(self):
        esperado = [("disponible", 13), ("en_remate", 1), ("vendida", 4), ("entregada", 8)]
        self.assertEqual(f.inventario_por_estado(), esperado)

    def test_stock_disponible_incluye_remate(self):
        self.assertEqual(len(f.stock_disponible()), 14)

    def test_stock_por_producto_suma_lo_mismo_que_el_stock(self):
        productos = f.stock_por_producto()
        self.assertEqual(sum(en_stock for _, _, en_stock, _ in productos), 14)
        # un producto por cada combinacion distinta de tipo + talla
        self.assertEqual(len(productos), self.contar("SELECT COUNT(*) FROM (SELECT DISTINCT tipo, talla FROM Prenda)"))

    def test_producto_vendido_completo_queda_sin_stock(self):
        prenda = {"tipo": "vestido rojo", "talla": "S", "costo": 2000, "precio_venta": 12000, "cantidad": 2}
        id_lote = f.registrar_lote(1, "2026-11-20", 4000, [prenda])
        ids = [fila[0] for fila in f.prendas_de_lote(id_lote)]
        self.assertIn(("vestido rojo", "S", 2, 0), f.stock_por_producto())
        f.registrar_venta(1, ids, "propia")
        self.assertIn(("vestido rojo", "S", 0, 0), f.stock_por_producto())

    def test_prenda_en_remate_cuenta_en_stock_y_en_remate(self):
        con = sqlite3.connect(self.ruta)
        tipo, talla = con.execute("SELECT tipo, talla FROM Prenda WHERE id_prenda = 10").fetchone()
        con.close()
        fila = [p for p in f.stock_por_producto() if p[0] == tipo and p[1] == talla][0]
        en_stock_esperado = self.contar(
            "SELECT COUNT(*) FROM Prenda WHERE tipo=? AND talla=? AND estado IN ('disponible','en_remate')",
            (tipo, talla))
        self.assertEqual(fila[2], en_stock_esperado)
        self.assertEqual(fila[3], 1)  # la prenda 10 es la unica en remate de los datos de prueba


class PruebasVenta(PruebaBase):
    def test_registrar_venta_descuenta_stock_y_calcula_margen(self):
        id_pedido = f.registrar_venta(1, [21, 22], "propia")
        self.assertEqual(
            self.contar("SELECT COUNT(*) FROM Prenda WHERE estado='vendida' AND id_prenda IN (21,22)"), 2)
        # prenda 21: precio 12000, costo 3000 -> margen 9000
        self.assertEqual(
            self.contar("SELECT margen FROM DetallePedido WHERE id_pedido=? AND id_prenda=21", (id_pedido,)), 9000)

    def test_venta_con_prenda_no_disponible_no_guarda_nada(self):
        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        with self.assertRaises(ValueError):
            f.registrar_venta(1, [21, 1], "propia")  # la prenda 1 ya esta entregada
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=21"), "disponible")

    def test_prenda_en_remate_se_cobra_a_precio_de_remate(self):
        id_pedido = f.registrar_venta(2, [10], "propia")  # prenda 10: remate 6000, costo 3000
        self.assertEqual(
            self.contar("SELECT precio_final FROM DetallePedido WHERE id_pedido=?", (id_pedido,)), 6000)
        self.assertEqual(
            self.contar("SELECT margen FROM DetallePedido WHERE id_pedido=?", (id_pedido,)), 3000)

    def test_marcar_entregado_actualiza_pedido_y_prendas(self):
        id_pedido = f.registrar_venta(1, [21], "propia")
        f.marcar_entregado(id_pedido)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=21"), "entregada")
        self.assertIsNotNone(
            self.contar("SELECT fecha_entrega FROM Pedido WHERE id_pedido=?", (id_pedido,)))


class PruebasAlertasYUmbral(PruebaBase):
    def test_umbral_se_lee_y_se_actualiza(self):
        self.assertEqual(f.obtener_umbral(), 30)
        f.actualizar_umbral(45)
        self.assertEqual(f.obtener_umbral(), 45)

    def test_atender_alerta_calcula_precio_de_remate(self):
        con = sqlite3.connect(self.ruta)
        con.execute("INSERT INTO AlertaRemate (id_prenda, fecha_alerta, dias_sin_venta, estado_alerta) "
                    "VALUES (7, date('now','localtime'), 60, 'pendiente')")
        id_alerta = con.execute("SELECT MAX(id_alerta) FROM AlertaRemate").fetchone()[0]
        con.commit()
        con.close()
        precio = f.atender_alerta(id_alerta, 1.0)  # costo 3000 con 100 % de margen
        self.assertEqual(precio, 6000)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=7"), "en_remate")
        self.assertEqual(
            self.contar("SELECT estado_alerta FROM AlertaRemate WHERE id_alerta=?", (id_alerta,)), "atendida")


if __name__ == "__main__":
    unittest.main()
