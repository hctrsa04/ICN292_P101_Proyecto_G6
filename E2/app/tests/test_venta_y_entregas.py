"""Pruebas de venta con clienta existente o nueva, busqueda de clientas,
prendas para venta y entregas pendientes. Usa base temporal.

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

CLIENTA_NUEVA = {"nombre": "Clienta Nueva", "contacto": "@nueva", "comuna": "Ñuñoa"}


class PruebasVentaConClientas(PruebaBase):
    def test_prenda_vendida_no_se_puede_vender_de_nuevo(self):
        f.registrar_venta(1, [21], "propia")
        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        with self.assertRaises(ValueError):
            f.registrar_venta(2, [21], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM DetallePedido WHERE id_prenda=21"), 1)

    def test_clienta_existente_no_crea_otra_fila(self):
        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        id_pedido = f.registrar_venta(3, [21], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes)
        self.assertEqual(self.contar("SELECT id_cliente FROM Pedido WHERE id_pedido=?", (id_pedido,)), 3)

    def test_clienta_nueva_se_crea_y_queda_en_el_pedido(self):
        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        id_pedido = f.registrar_venta(CLIENTA_NUEVA, [21, 22], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes + 1)
        self.assertEqual(self.contar(
            "SELECT c.nombre FROM Pedido p JOIN Cliente c ON p.id_cliente = c.id_cliente "
            "WHERE p.id_pedido=?", (id_pedido,)), "Clienta Nueva")

    def test_contacto_repetido_crea_otra_clienta(self):
        # Regla R3: el contacto no es unico y no se asocia automaticamente
        clienta = {"nombre": "Otra persona", "contacto": "@clienta1", "comuna": ""}
        f.registrar_venta(clienta, [21], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente WHERE contacto='@clienta1'"), 2)
        # comuna vacia se guarda como NULL
        self.assertIsNone(self.contar("SELECT comuna FROM Cliente WHERE nombre='Otra persona'"))

    def test_si_la_venta_falla_no_queda_la_clienta_nueva_ni_el_pedido(self):
        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        with self.assertRaises(ValueError):
            # la 21 esta disponible, pero la 1 ya esta entregada: falla despues de crear la clienta
            f.registrar_venta(CLIENTA_NUEVA, [21, 1], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente WHERE nombre='Clienta Nueva'"), 0)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=21"), "disponible")

    def test_validaciones_no_guardan_nada(self):
        casos = [
            (1, [], "propia", None),                       # sin prendas
            (1, [21, 21], "propia", None),                 # prenda repetida
            (1, [999], "propia", None),                    # prenda que no existe
            (1, [21], "a domicilio", None),                # tipo de entrega no valido
            (1, [21], "distribuidor", None),               # distribuidor sin elegir
            (1, [21], "distribuidor", 99),                 # distribuidor que no existe
            (99, [21], "propia", None),                    # clienta que no existe
            ({"nombre": "  ", "contacto": "@x"}, [21], "propia", None),  # clienta nueva sin nombre
        ]
        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        for caso in casos:
            with self.subTest(caso=caso):
                with self.assertRaises(ValueError):
                    f.registrar_venta(*caso)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=21"), "disponible")

    def test_entrega_propia_no_guarda_distribuidor(self):
        id_pedido = f.registrar_venta(1, [21], "propia", 1)
        self.assertIsNone(self.contar("SELECT id_distribuidor FROM Pedido WHERE id_pedido=?", (id_pedido,)))

    def test_venta_por_distribuidor(self):
        id_pedido = f.registrar_venta(1, [21], "distribuidor", 2)
        self.assertEqual(self.contar("SELECT id_distribuidor FROM Pedido WHERE id_pedido=?", (id_pedido,)), 2)


class PruebasBusquedasYListas(PruebaBase):
    def test_buscar_clientas_por_nombre_y_contacto(self):
        self.assertEqual([c[0] for c in f.buscar_clientas("prueba 2")], [2])
        self.assertEqual([c[0] for c in f.buscar_clientas("@CLIENTA3")], [3])  # sin importar mayusculas
        self.assertEqual(len(f.buscar_clientas("")), 4)
        self.assertEqual(f.buscar_clientas("no existe nadie"), [])

    def test_listar_distribuidores(self):
        self.assertEqual(f.listar_distribuidores(),
                         [(1, "Agencia de delivery 1"), (2, "Agencia de delivery 2")])

    def test_prendas_para_venta(self):
        prendas = {fila[0]: fila for fila in f.prendas_para_venta()}
        self.assertEqual(len(prendas), 14)
        # prenda 10 en remate: se cobra 6000 (no 12000), costo 3000 -> margen 3000
        self.assertEqual(prendas[10][3:], ("en_remate", 6000, 3000))
        # prenda 21 disponible: precio 12000, costo 3000 -> margen 9000
        self.assertEqual(prendas[21][3:], ("disponible", 12000, 9000))
        self.assertNotIn(1, prendas)  # entregada
        self.assertNotIn(6, prendas)  # vendida

    def test_obtener_pedido(self):
        id_pedido = f.registrar_venta(1, [21, 10], "propia")  # 12000 + 6000 (remate)
        self.assertEqual(f.obtener_pedido(id_pedido)[1:],
                         ("Clienta Prueba 1", self.contar("SELECT date('now','localtime')"), 2, 18000, 12000))


def producto(tipo, talla, precio, cantidad, estado="disponible"):
    return {"tipo": tipo, "talla": talla, "estado": estado, "precio": precio, "cantidad": cantidad}


class PruebasVentaPorProducto(PruebaBase):
    def test_productos_para_venta(self):
        productos = f.productos_para_venta()
        self.assertEqual(sum(fila[4] for fila in productos), 14)
        # blusa M a $12.000 tiene 2 unidades (prendas 7 y 22); la de $13.000 va aparte
        self.assertIn(("blusa", "M", "disponible", 12000, 2), productos)
        self.assertIn(("blusa", "M", "disponible", 13000, 1), productos)
        # la blusa L en remate es una linea aparte, a precio de remate
        self.assertIn(("blusa", "L", "en_remate", 6000, 1), productos)

    def test_elegir_prendas_toma_las_mas_antiguas(self):
        # abrigo M $18.000: prenda 15 (lote de hace 35 dias) y 26 (hace 10 dias)
        self.assertEqual(f.elegir_prendas([producto("abrigo", "M", 18000, 1)]), [15])
        self.assertEqual(f.elegir_prendas([producto("abrigo", "M", 18000, 2)]), [15, 26])

    def test_mismo_producto_dos_veces_suma_cantidades(self):
        ids = f.elegir_prendas([producto("abrigo", "M", 18000, 1), producto("abrigo", "M", 18000, 1)])
        self.assertEqual(ids, [15, 26])

    def test_no_se_pueden_pedir_mas_unidades_que_el_stock(self):
        with self.assertRaises(ValueError) as error:
            f.elegir_prendas([producto("abrigo", "M", 18000, 3)])
        self.assertIn("Solo quedan 2", str(error.exception))

    def test_vender_por_producto_descuenta_unidades(self):
        id_pedido = f.registrar_venta_por_producto(
            1, [producto("blusa", "M", 12000, 2), producto("blusa", "L", 6000, 1, "en_remate")], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM DetallePedido WHERE id_pedido=?", (id_pedido,)), 3)
        self.assertNotIn(("blusa", "M", "disponible", 12000, 2), f.productos_para_venta())
        # la de remate se cobra a 6000 (R4)
        self.assertEqual(self.contar("SELECT precio_final FROM DetallePedido WHERE id_prenda=10"), 6000)

    def test_pedir_de_mas_no_guarda_nada_ni_la_clienta_nueva(self):
        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        with self.assertRaises(ValueError):
            f.registrar_venta_por_producto(
                CLIENTA_NUEVA, [producto("blusa", "S", 12000, 1), producto("abrigo", "M", 18000, 5)], "propia")
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=21"), "disponible")

    def test_cantidad_o_producto_invalido(self):
        for productos in ([], [producto("abrigo", "M", 18000, 0)], [producto("abrigo", "M", 18000, 1, "vendida")]):
            with self.subTest(productos=productos):
                with self.assertRaises(ValueError):
                    f.elegir_prendas(productos)


class PruebasEntregasPendientes(PruebaBase):
    def test_pendientes_de_los_datos_de_prueba(self):
        pendientes = f.pedidos_pendientes_entrega()
        self.assertEqual([p[0] for p in pendientes], [6, 7])  # el mas antiguo primero
        pedido_6, pedido_7 = pendientes
        self.assertEqual(pedido_6[2], "Clienta Prueba 2")
        self.assertEqual(pedido_6[4:6], ("propia", None))
        self.assertEqual(pedido_6[7], 28000)  # 12000 + 16000
        self.assertEqual(pedido_6[8], 5)      # vendido hace 5 dias
        self.assertEqual(pedido_7[5], "Agencia de delivery 2")

    def test_venta_nueva_aparece_y_al_entregar_sale(self):
        id_pedido = f.registrar_venta(1, [21], "propia")
        self.assertIn(id_pedido, [p[0] for p in f.pedidos_pendientes_entrega()])
        f.marcar_entregado(id_pedido)
        self.assertNotIn(id_pedido, [p[0] for p in f.pedidos_pendientes_entrega()])
        f.marcar_entregado(6)
        self.assertEqual([p[0] for p in f.pedidos_pendientes_entrega()], [7])


if __name__ == "__main__":
    unittest.main()
