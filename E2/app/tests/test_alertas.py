"""Pruebas de generar_alertas (alerta_remate.py), umbral y atender_alerta.
Usa base temporal: nunca toca data/altafacha.db.

Ejecutar desde la carpeta raiz del proyecto:

    python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import sys
import unittest

CARPETA_TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CARPETA_TESTS))  # raiz: funciones_bd.py, alerta_remate.py
sys.path.insert(0, CARPETA_TESTS)                   # test_funciones_bd.py

import alerta_remate  # noqa: E402
import funciones_bd as f  # noqa: E402
from test_funciones_bd import PruebaBase  # noqa: E402

# Con la base de prueba y umbral 30: lote de hace 60 dias (prendas 7, 8, 9) y
# lote de hace 35 dias (15, 16, 17, 18). La 10 esta en remate y no se alerta.
PRENDAS_60_DIAS = [7, 8, 9]
PRENDAS_35_DIAS = [15, 16, 17, 18]


class PruebasGenerarAlertas(PruebaBase):
    def test_con_la_base_de_prueba_crea_7(self):
        nuevas = alerta_remate.generar_alertas(self.ruta)
        self.assertEqual(sorted(a[0] for a in nuevas), PRENDAS_60_DIAS + PRENDAS_35_DIAS)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM AlertaRemate WHERE estado_alerta='pendiente'"), 7)

    def test_es_idempotente(self):
        alerta_remate.generar_alertas(self.ruta)
        self.assertEqual(alerta_remate.generar_alertas(self.ruta), [])
        self.assertEqual(self.contar("SELECT COUNT(*) FROM AlertaRemate WHERE estado_alerta='pendiente'"), 7)

    def test_umbral_40_crea_solo_las_de_60_dias(self):
        f.actualizar_umbral(40)
        nuevas = alerta_remate.generar_alertas(self.ruta)
        self.assertEqual(sorted(a[0] for a in nuevas), PRENDAS_60_DIAS)

    def test_no_alerta_prendas_en_remate_ni_vendidas(self):
        nuevas = [a[0] for a in alerta_remate.generar_alertas(self.ruta)]
        self.assertNotIn(10, nuevas)  # en remate
        self.assertNotIn(6, nuevas)   # vendida (lote de hace 60 dias)

    def test_devuelve_tipo_talla_y_dias(self):
        nuevas = {a[0]: a for a in alerta_remate.generar_alertas(self.ruta)}
        self.assertEqual(nuevas[7], (7, "blusa", "M", 60))
        self.assertEqual(nuevas[15], (15, "abrigo", "M", 35))

    def test_imprime_lo_mismo_que_antes(self):
        hoy = self.contar("SELECT date('now','localtime')")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            alerta_remate.generar_alertas(self.ruta, mostrar=True)
        lineas = salida.getvalue().splitlines()
        self.assertEqual(lineas[0], "Revision del " + hoy + " - umbral: 30 dias")
        self.assertIn("Alerta generada: prenda 7 - blusa M - 60 dias sin venta", lineas)
        self.assertEqual(lineas[-1], "Total alertas nuevas: 7")
        self.assertEqual(len(lineas), 9)  # encabezado + 7 alertas + total

        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            alerta_remate.generar_alertas(self.ruta, mostrar=True)
        self.assertEqual(salida.getvalue().splitlines()[1], "Sin prendas para remate")

    def test_sin_mostrar_no_imprime(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            alerta_remate.generar_alertas(self.ruta)
        self.assertEqual(salida.getvalue(), "")


class PruebasUmbral(PruebaBase):
    def test_umbral_invalido_no_cambia_nada(self):
        for valor in (0, -5, "40", 2.5, None, True):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    f.actualizar_umbral(valor)
        self.assertEqual(f.obtener_umbral(), 30)


class PruebasAtenderAlerta(PruebaBase):
    def alerta_de(self, id_prenda):
        return self.contar("SELECT id_alerta FROM AlertaRemate WHERE id_prenda=? AND estado_alerta='pendiente'",
                           (id_prenda,))

    def test_atender_con_100_por_ciento_deja_el_doble_del_costo(self):
        alerta_remate.generar_alertas(self.ruta)
        precio = f.atender_alerta(self.alerta_de(7), 1.0)  # costo 3000
        self.assertEqual(precio, 6000)
        self.assertEqual(self.contar("SELECT precio_remate FROM Prenda WHERE id_prenda=7"), 6000)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=7"), "en_remate")
        # deja de estar pendiente y la prenda en remate no se vuelve a alertar
        self.assertNotIn(7, [a[1] for a in f.alertas_pendientes()])
        self.assertEqual(alerta_remate.generar_alertas(self.ruta), [])

    def test_calcular_precio_remate(self):
        self.assertEqual(f.calcular_precio_remate(3000, 1.0), 6000)
        self.assertEqual(f.calcular_precio_remate(3500, 0.5), 5250)
        self.assertEqual(f.calcular_precio_remate(3000, 0), 3000)

    def test_margen_invalido_no_cambia_nada(self):
        alerta_remate.generar_alertas(self.ruta)
        id_alerta = self.alerta_de(7)
        for margen in (-0.1, "1.0", None, True):
            with self.subTest(margen=margen):
                with self.assertRaises(ValueError):
                    f.atender_alerta(id_alerta, margen)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=7"), "disponible")

    def test_alerta_ya_atendida_no_se_atiende_de_nuevo(self):
        alerta_remate.generar_alertas(self.ruta)
        id_alerta = self.alerta_de(7)
        f.atender_alerta(id_alerta, 1.0)
        with self.assertRaises(ValueError):
            f.atender_alerta(id_alerta, 0.5)
        self.assertEqual(self.contar("SELECT precio_remate FROM Prenda WHERE id_prenda=7"), 6000)

    def test_prenda_vendida_con_alerta_pendiente(self):
        # Arreglo aprobado: si se vende antes de atender la alerta, no se muestra ni se
        # puede poner en remate (volveria al stock y se podria vender dos veces).
        alerta_remate.generar_alertas(self.ruta)
        id_alerta = self.alerta_de(7)
        f.registrar_venta(1, [7], "propia")
        self.assertNotIn(7, [a[1] for a in f.alertas_pendientes()])
        self.assertEqual(len(f.alertas_pendientes()), 6)
        with self.assertRaises(ValueError):
            f.atender_alerta(id_alerta, 1.0)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=7"), "vendida")

    def test_alerta_que_no_existe(self):
        with self.assertRaises(ValueError):
            f.atender_alerta(999, 1.0)


if __name__ == "__main__":
    unittest.main()
