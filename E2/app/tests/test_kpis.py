"""Pruebas de kpis.py (K1 a K5) con la base de prueba.
Los valores esperados son los de ../docs/05-kpi-dashboard.md. Usa base temporal.

Ejecutar desde la carpeta raiz del proyecto:

    python -m unittest discover -s tests -v
"""
import hashlib
import os
import sqlite3
import sys
import unittest

CARPETA_TESTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CARPETA_TESTS))  # raiz: kpis.py, funciones_bd.py
sys.path.insert(0, CARPETA_TESTS)                   # test_funciones_bd.py

import funciones_bd as f  # noqa: E402
import kpis  # noqa: E402
from test_funciones_bd import PruebaBase  # noqa: E402


class PruebasKpi(PruebaBase):
    def test_k1_inventario_por_estado(self):
        k1 = kpis.k1_inventario_por_estado()
        self.assertEqual(list(zip(k1["estado"], k1["prendas"])),
                         [("disponible", 13), ("en_remate", 1), ("vendida", 4), ("entregada", 8)])

    def test_k1_estado_sin_prendas_aparece_con_0(self):
        con = sqlite3.connect(self.ruta)
        con.execute("UPDATE Prenda SET estado = 'disponible' WHERE estado = 'en_remate'")
        con.commit()
        con.close()
        k1 = kpis.k1_inventario_por_estado()
        self.assertEqual(list(k1["estado"]), kpis.ESTADOS)
        self.assertEqual(int(k1.loc[k1["estado"] == "en_remate", "prendas"].iloc[0]), 0)

    def test_k2_totales(self):
        # No se fija el reparto por mes: depende del dia en que se crea la base
        k2 = kpis.k2_ventas_margen_mensual()
        self.assertEqual(int(k2["prendas_vendidas"].sum()), 12)
        self.assertEqual(int(k2["ventas"].sum()), 183000)
        self.assertEqual(int(k2["margen"].sum()), 145000)
        self.assertEqual(list(k2.columns), ["mes", "prendas_vendidas", "ventas", "margen"])

    def test_k3_margen_bruto(self):
        k3 = kpis.k3_margen_bruto().iloc[0]
        self.assertEqual(k3["margen_pct"], 79.2)
        self.assertEqual(k3["margen_medio_prenda"], 12083)
        self.assertEqual(int(k3["prendas_vendidas"]), 12)

    def test_k4_recuperacion_por_lote(self):
        k4 = kpis.k4_recuperacion_por_lote()
        self.assertEqual(list(k4["id_lote"]), [1, 2, 3])
        self.assertEqual(list(k4["veces_inversion"]), [2.83, 2.43, 1.25])
        self.assertEqual(list(k4["resultado_neto"]), [55000, 40000, 6000])
        self.assertEqual(list(k4["ventas"]), [85000, 68000, 30000])
        self.assertEqual(list(k4["pct_vendido"]), [60.0, 50.0, 25.0])
        # meta >= 2,0: lotes 1 y 2 si, lote 3 aun no
        self.assertEqual(list(k4["veces_inversion"] >= kpis.META_K4), [True, True, False])

    def test_k5_umbral_30_y_50(self):
        k5 = kpis.k5_stock_sobre_umbral().iloc[0]
        self.assertEqual((int(k5["sobre_umbral"]), int(k5["disponibles"])), (7, 13))
        self.assertEqual(k5["pct_sobre_umbral"], 53.8)
        self.assertEqual(int(k5["umbral_dias"]), 30)
        f.actualizar_umbral(50)
        k5 = kpis.k5_stock_sobre_umbral().iloc[0]
        self.assertEqual((int(k5["sobre_umbral"]), int(k5["disponibles"])), (3, 13))
        self.assertEqual(k5["pct_sobre_umbral"], 23.1)

    def test_kpi_no_escriben_en_la_base(self):
        with open(self.ruta, "rb") as fh:
            antes = hashlib.sha256(fh.read()).hexdigest()
        for funcion in (kpis.k1_inventario_por_estado, kpis.k2_ventas_margen_mensual,
                        kpis.k3_margen_bruto, kpis.k4_recuperacion_por_lote, kpis.k5_stock_sobre_umbral):
            funcion()
        with open(self.ruta, "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), antes)

    def test_sin_ventas_no_falla(self):
        con = sqlite3.connect(self.ruta)
        con.execute("DELETE FROM DetallePedido")
        con.commit()
        con.close()
        self.assertTrue(kpis.k2_ventas_margen_mensual().empty)
        self.assertTrue(kpis.k3_margen_bruto()["margen_pct"].isna().iloc[0])
        self.assertEqual(list(kpis.k4_recuperacion_por_lote()["veces_inversion"]), [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
