"""Pruebas de registrar_lote() (RF-01, RF-02) con base temporal.

Ejecutar desde la carpeta raiz del proyecto:

    python -m unittest discover -s tests -v
"""
import os
import sqlite3
import sys
import unittest

CARPETA_TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CARPETA_TESTS))  # raiz: funciones_bd.py
sys.path.insert(0, CARPETA_TESTS)                   # test_funciones_bd.py

import funciones_bd as f  # noqa: E402
from test_funciones_bd import PruebaBase  # noqa: E402

FECHA = "2026-11-20"


def prendas_ejemplo():
    # Costos distintos entre si y que NO suman el costo total (20000): asi se
    # comprueba que cada prenda guarda su costo y no un reparto del lote (R1).
    return [
        {"tipo": "vestido", "talla": "M", "costo": 2000, "precio_venta": 12000},
        {"tipo": "blusa", "talla": "S", "costo": 3500, "precio_venta": 10000},
        {"tipo": "abrigo", "talla": "L", "costo": 5000, "precio_venta": 20000},
    ]


class PruebasRegistrarLote(PruebaBase):
    def test_crea_una_prenda_disponible_por_cada_elemento(self):
        id_lote = f.registrar_lote(1, FECHA, 20000, prendas_ejemplo())
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Prenda WHERE id_lote=?", (id_lote,)), 3)
        self.assertEqual(self.contar(
            "SELECT COUNT(*) FROM Prenda WHERE id_lote=? AND estado='disponible'", (id_lote,)), 3)
        self.assertEqual(self.contar("SELECT cantidad_prendas FROM Lote WHERE id_lote=?", (id_lote,)), 3)

    def test_cada_prenda_guarda_su_costo_individual(self):
        id_lote = f.registrar_lote(1, FECHA, 20000, prendas_ejemplo())
        guardadas = [(tipo, talla, costo, precio) for _, tipo, talla, costo, precio, _
                     in f.prendas_de_lote(id_lote)]
        self.assertEqual(guardadas, [
            ("vestido", "M", 2000, 12000),
            ("blusa", "S", 3500, 10000),
            ("abrigo", "L", 5000, 20000),
        ])

    def test_lote_guarda_su_costo_total_y_fecha(self):
        id_lote = f.registrar_lote(2, FECHA, 20000, prendas_ejemplo())
        lote = f.obtener_lote(id_lote)
        self.assertEqual(lote, (id_lote, "Mayorista Fardos B", FECHA, 20000, 3))

    def test_proveedor_nuevo_se_crea(self):
        antes = self.contar("SELECT COUNT(*) FROM Proveedor")
        id_lote = f.registrar_lote("  Feria Persa  ", FECHA, 20000, prendas_ejemplo())
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Proveedor"), antes + 1)
        self.assertEqual(f.obtener_lote(id_lote)[1], "Feria Persa")
        self.assertIn("Feria Persa", [nombre for _, nombre in f.listar_proveedores()])

    def test_proveedor_existente_no_se_duplica(self):
        antes = self.contar("SELECT COUNT(*) FROM Proveedor")
        f.registrar_lote(1, FECHA, 20000, prendas_ejemplo())
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Proveedor"), antes)

    def test_validaciones_no_guardan_nada(self):
        casos = [
            (1, FECHA, 0, prendas_ejemplo()),                 # costo total 0
            (1, FECHA, 20000, []),                            # sin prendas
            (1, FECHA, 20000, [{"tipo": " ", "talla": "M", "costo": 1000, "precio_venta": 5000}]),
            (1, FECHA, 20000, [{"tipo": "falda", "talla": "", "costo": 1000, "precio_venta": 5000}]),
            (1, FECHA, 20000, [{"tipo": "falda", "talla": "M", "costo": 0, "precio_venta": 5000}]),
            (1, FECHA, 20000, [{"tipo": "falda", "talla": "M", "costo": 1000, "precio_venta": -1}]),
            (1, FECHA, 20000, [{"tipo": "falda", "talla": "M", "costo": None, "precio_venta": 5000}]),
            (1, "20/11/2026", 20000, prendas_ejemplo()),      # fecha mal escrita
            (999, FECHA, 20000, prendas_ejemplo()),           # proveedor que no existe
            ("   ", FECHA, 20000, prendas_ejemplo()),         # proveedor nuevo sin nombre
        ]
        lotes_antes = self.contar("SELECT COUNT(*) FROM Lote")
        prendas_antes = self.contar("SELECT COUNT(*) FROM Prenda")
        for caso in casos:
            with self.subTest(caso=caso):
                with self.assertRaises(ValueError):
                    f.registrar_lote(*caso)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Lote"), lotes_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Prenda"), prendas_antes)

    def test_cantidad_crea_una_ficha_por_unidad(self):
        prendas = [
            {"tipo": "vestido rojo", "talla": "S", "costo": 2000, "precio_venta": 12000, "cantidad": 10},
            {"tipo": "blusa", "talla": "M", "costo": 3000, "precio_venta": 10000},  # sin cantidad = 1
        ]
        id_lote = f.registrar_lote(1, FECHA, 25000, prendas)
        self.assertEqual(self.contar("SELECT cantidad_prendas FROM Lote WHERE id_lote=?", (id_lote,)), 11)
        self.assertEqual(self.contar(
            "SELECT COUNT(*) FROM Prenda WHERE id_lote=? AND tipo='vestido rojo' AND talla='S' "
            "AND costo=2000 AND precio_venta=12000 AND estado='disponible'", (id_lote,)), 10)
        self.assertEqual(self.contar(
            "SELECT COUNT(*) FROM Prenda WHERE id_lote=? AND tipo='blusa'", (id_lote,)), 1)

    def test_cantidad_invalida_no_guarda_nada(self):
        prendas_antes = self.contar("SELECT COUNT(*) FROM Prenda")
        for cantidad in (0, -3, "10", 2.5):
            with self.subTest(cantidad=cantidad):
                prenda = {"tipo": "falda", "talla": "M", "costo": 1000, "precio_venta": 5000,
                          "cantidad": cantidad}
                with self.assertRaises(ValueError):
                    f.registrar_lote(1, FECHA, 20000, [prenda])
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Prenda"), prendas_antes)

    def test_tipo_y_talla_sin_mayusculas_tildes_ni_espacios_extra(self):
        prendas = [
            {"tipo": "  Vestido   ROJO ", "talla": "s", "costo": 2000, "precio_venta": 12000},
            {"tipo": "POLERÓN", "talla": "xl", "costo": 2000, "precio_venta": 12000},
            {"tipo": "Pañuelo", "talla": "única", "costo": 2000, "precio_venta": 12000},
        ]
        id_lote = f.registrar_lote(1, FECHA, 6000, prendas)
        guardadas = [(tipo, talla) for _, tipo, talla, _, _, _ in f.prendas_de_lote(id_lote)]
        # la ñ se mantiene; solo se quitan las tildes
        self.assertEqual(guardadas, [("vestido rojo", "S"), ("poleron", "XL"), ("pañuelo", "UNICA")])

    def test_falla_a_mitad_no_deja_datos_a_medias(self):
        # Trigger solo en la base temporal: hace fallar el INSERT de la segunda prenda,
        # cuando ya se insertaron el proveedor nuevo, el lote y la primera prenda.
        con = sqlite3.connect(self.ruta)
        con.execute("""
            CREATE TRIGGER falla_forzada BEFORE INSERT ON Prenda
            WHEN NEW.tipo = 'blusa'
            BEGIN SELECT RAISE(ABORT, 'falla forzada'); END
        """)
        con.commit()
        con.close()

        proveedores_antes = self.contar("SELECT COUNT(*) FROM Proveedor")
        lotes_antes = self.contar("SELECT COUNT(*) FROM Lote")
        prendas_antes = self.contar("SELECT COUNT(*) FROM Prenda")
        with self.assertRaises(sqlite3.Error):
            f.registrar_lote("Proveedor que no debe quedar", FECHA, 20000, prendas_ejemplo())
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Proveedor"), proveedores_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Lote"), lotes_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Prenda"), prendas_antes)


if __name__ == "__main__":
    unittest.main()
