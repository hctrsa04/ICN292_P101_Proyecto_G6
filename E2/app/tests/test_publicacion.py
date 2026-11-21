"""Pruebas de generar_ficha_publicacion (RF-06). Usa base temporal.

Ejecutar desde la carpeta raiz del proyecto:

    python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

CARPETA_TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CARPETA_TESTS))  # raiz: funciones_bd.py
sys.path.insert(0, CARPETA_TESTS)                   # test_funciones_bd.py

import funciones_bd as f  # noqa: E402
from test_funciones_bd import PruebaBase  # noqa: E402

# Productos de los datos de prueba (como los agrupa productos_para_venta)
BLUSA_M = {"tipo": "blusa", "talla": "M", "estado": "disponible", "precio": 12000}   # prendas 7 y 22
BLUSA_L_REMATE = {"tipo": "blusa", "talla": "L", "estado": "en_remate", "precio": 6000}  # prenda 10


class PruebasFichaPublicacion(PruebaBase):
    def test_ficha_de_producto_disponible(self):
        texto, unidades = f.generar_ficha_publicacion(BLUSA_M)
        self.assertEqual(unidades, 2)
        self.assertEqual(texto, "✨ Blusa · Talla M ✨\n💰 $12.000\n📩 Escríbenos por DM para comprarla")
        self.assertNotIn("REMATE", texto)

    def test_ficha_en_remate_muestra_precio_de_remate(self):
        texto, unidades = f.generar_ficha_publicacion(BLUSA_L_REMATE)
        self.assertEqual(unidades, 1)
        self.assertEqual(texto.splitlines(), [
            "🔥 ¡REMATE! 🔥",
            "✨ Blusa · Talla L ✨",
            "💰 Antes $12.000 → Ahora $6.000",
            "📩 Escríbenos por DM para comprarla",
        ])

    def test_guarda_una_publicacion_por_unidad_con_fecha_de_hoy(self):
        hoy = self.contar("SELECT date('now','localtime')")
        texto, _ = f.generar_ficha_publicacion(BLUSA_M)
        for id_prenda in (7, 22):
            with self.subTest(id_prenda=id_prenda):
                self.assertEqual(self.contar(
                    "SELECT COUNT(*) FROM Publicacion WHERE id_prenda=? AND fecha_publicacion=? "
                    "AND descripcion=?", (id_prenda, hoy, texto)), 1)
        self.assertEqual(f.ultima_publicacion(BLUSA_M), hoy)

    def test_una_prenda_puede_tener_varias_publicaciones(self):
        antes = self.contar("SELECT COUNT(*) FROM Publicacion WHERE id_prenda=10")  # 1 del seed
        f.generar_ficha_publicacion(BLUSA_L_REMATE)
        f.generar_ficha_publicacion(BLUSA_L_REMATE)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Publicacion WHERE id_prenda=10"), antes + 2)

    def test_producto_vendido_o_inexistente_no_guarda_nada(self):
        casos = [
            {"tipo": "blusa", "talla": "S", "estado": "vendida", "precio": 12000},
            {"tipo": "no existe", "talla": "M", "estado": "disponible", "precio": 12000},
            {"tipo": "blusa", "talla": "M", "estado": "disponible", "precio": 99999},  # otro precio
        ]
        antes = self.contar("SELECT COUNT(*) FROM Publicacion")
        for producto in casos:
            with self.subTest(producto=producto):
                with self.assertRaises(ValueError):
                    f.generar_ficha_publicacion(producto)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Publicacion"), antes)

    def test_producto_vendido_completo_ya_no_se_publica(self):
        f.registrar_venta_por_producto(1, [dict(BLUSA_L_REMATE, cantidad=1)], "propia")
        with self.assertRaises(ValueError):
            f.generar_ficha_publicacion(BLUSA_L_REMATE)

    def test_ultima_publicacion_sin_publicaciones(self):
        f.registrar_lote(1, "2026-11-21", 5000, [{"tipo": "falda", "talla": "XS", "costo": 2000,
                                                 "precio_venta": 9000}])
        self.assertIsNone(f.ultima_publicacion(
            {"tipo": "falda", "talla": "XS", "estado": "disponible", "precio": 9000}))


if __name__ == "__main__":
    unittest.main()
