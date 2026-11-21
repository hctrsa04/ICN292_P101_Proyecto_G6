"""Pruebas del esqueleto de la app Streamlit (app/main.py).

Usa AppTest, que viene incluido en Streamlit (no es una dependencia nueva):
ejecuta la app sin abrir el navegador. Igual que test_funciones_bd.py, usa una
base temporal y nunca toca data/altafacha.db.
"""
import os
import sqlite3
import sys
import tempfile
import unittest

from streamlit.testing.v1 import AppTest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import funciones_bd as f  # noqa: E402
from test_funciones_bd import crear_base_temporal  # noqa: E402

RUTA_APP = os.path.join(RAIZ, "app", "main.py")
CLAVE_PRUEBA = "clave-de-prueba"  # solo para tests; AppTest simula st.secrets sin crear archivos


def app_con_sesion():
    # App con la clave configurada y la sesion ya iniciada (para probar las pantallas)
    app = AppTest.from_file(RUTA_APP)
    app.secrets["clave_acceso"] = CLAVE_PRUEBA
    app.session_state["autenticada"] = True
    return app


class PruebasEsqueleto(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "prueba.db")
        self.ruta_original = f.ruta_bd
        f.ruta_bd = self.ruta  # la app usa el mismo modulo funciones_bd

    def tearDown(self):
        f.ruta_bd = self.ruta_original
        self.carpeta.cleanup()

    def test_app_carga_sin_errores(self):
        crear_base_temporal(self.ruta)
        app = app_con_sesion().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.title[0].value, "Alta Facha — SIG")
        self.assertEqual(len(app.error), 0)

    def test_sin_base_muestra_mensaje(self):
        # no se crea la base temporal: la app debe avisar y no crear un archivo vacio
        app = app_con_sesion().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("crear_bd.py", app.error[0].value)
        self.assertFalse(os.path.exists(self.ruta))


class PruebaPantalla(unittest.TestCase):
    # Base para probar pantallas: base temporal con datos de prueba. No tiene tests propios.
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "prueba.db")
        crear_base_temporal(self.ruta)
        self.ruta_original = f.ruta_bd
        f.ruta_bd = self.ruta

    def tearDown(self):
        f.ruta_bd = self.ruta_original
        self.carpeta.cleanup()

    def abrir(self, pagina):
        app = app_con_sesion().run()
        app.switch_page(pagina).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def boton(self, app, texto):
        return [b for b in app.button if b.label == texto][0]

    def contar(self, sql, params=()):
        con = sqlite3.connect(self.ruta)
        try:
            return con.execute(sql, params).fetchone()[0]
        finally:
            con.close()


class PruebasPantallasEtapa1(PruebaPantalla):
    def test_inventario_muestra_resumen_por_estado(self):
        app = self.abrir("paginas/inventario.py")
        valores = {m.label: m.value for m in app.metric}
        self.assertEqual(valores, {"Stock para vender": "14", "Disponible": "13",
                                   "En remate": "1", "Vendida": "4", "Entregada": "8"})
        # tabla 0 = stock por producto, tabla 1 = detalle por prenda (dentro del desplegable)
        self.assertEqual(len(app.dataframe[0].value), len(f.stock_por_producto()))
        self.assertEqual(len(app.dataframe[1].value), 14)

    def test_inventario_filtra_por_tipo(self):
        app = self.abrir("paginas/inventario.py")
        app.selectbox[0].select("vestido").run()
        productos = app.dataframe[0].value
        detalle = app.dataframe[1].value
        self.assertGreater(len(productos), 0)
        self.assertTrue((productos["Prenda"] == "vestido").all())
        self.assertTrue((detalle["Tipo"] == "vestido").all())

    def test_inventario_muestra_y_oculta_productos_sin_stock(self):
        prenda = {"tipo": "vestido azul", "talla": "S", "costo": 2000, "precio_venta": 12000}
        id_lote = f.registrar_lote(1, "2026-11-20", 2000, [prenda])
        f.registrar_venta(1, [f.prendas_de_lote(id_lote)[0][0]], "propia")

        app = self.abrir("paginas/inventario.py")
        productos = app.dataframe[0].value
        fila = productos[productos["Prenda"] == "vestido azul"]
        self.assertEqual(fila["Stock"].tolist(), ["Sin stock"])

        app.checkbox[0].uncheck().run()
        productos = app.dataframe[0].value
        self.assertNotIn("Sin stock", productos["Stock"].tolist())
        self.assertNotIn("vestido azul", productos["Prenda"].tolist())

    def test_registrar_lote_desde_la_pantalla(self):
        app = self.abrir("paginas/registrar_lote.py")
        app.selectbox(key="proveedor").select("➕ Proveedor nuevo").run()
        app.text_input(key="nombre_proveedor_nuevo").input("Proveedor de prueba")
        app.number_input(key="costo_total").set_value(5000)
        # 3 vestidos iguales + 1 falda (escrita con mayusculas y talla en minuscula)
        for tipo, talla, cantidad, costo in (("vestido", "M", 3, 2000), ("FALDA", "s", 1, 2500)):
            app.text_input(key="prenda_tipo").input(tipo)
            app.text_input(key="prenda_talla").input(talla)
            app.number_input(key="prenda_cantidad").set_value(cantidad)
            app.number_input(key="prenda_costo").set_value(costo)
            app.number_input(key="prenda_precio").set_value(10000)
            self.boton(app, "Agregar prenda").click().run()
        self.assertEqual(len(app.session_state["prendas_lote"]), 2)
        # la suma (3 x 2000 + 2500 = 8500) es distinta del costo total (5000): aviso P1, no bloquea
        self.assertIn("$8.500", app.info[0].value)

        self.boton(app, "Guardar lote").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("4 prendas de Proveedor de prueba", app.success[0].value)

        con = sqlite3.connect(self.ruta)
        guardadas = con.execute(
            "SELECT p.tipo, p.talla, p.costo FROM Prenda p JOIN Lote l ON p.id_lote = l.id_lote "
            "JOIN Proveedor pr ON l.id_proveedor = pr.id_proveedor "
            "WHERE pr.nombre = 'Proveedor de prueba' ORDER BY p.id_prenda").fetchall()
        con.close()
        self.assertEqual(guardadas, [("vestido", "M", 2000)] * 3 + [("falda", "S", 2500)])

    def test_registrar_lote_sin_prendas_muestra_error(self):
        app = self.abrir("paginas/registrar_lote.py")
        app.number_input(key="costo_total").set_value(5000)
        self.boton(app, "Guardar lote").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("al menos 1 prenda", app.error[0].value)


class PruebasPantallasEtapa2(PruebaPantalla):
    def agregar(self, app, producto, unidades):
        # producto = (tipo, talla, estado, precio), igual que productos_para_venta()
        app.selectbox(key="producto_venta").select(producto).run()
        app.number_input(key="cantidad_venta").set_value(unidades)
        self.boton(app, "Agregar a la venta").click().run()

    def confirmar(self, app):
        app.checkbox(key="confirmo_venta").check().run()
        self.boton(app, "Confirmar venta").click().run()

    def test_venta_por_producto_con_clienta_nueva_y_doble_clic(self):
        app = self.abrir("paginas/registrar_venta.py")
        app.radio(key="tipo_clienta").set_value("Clienta nueva").run()
        app.text_input(key="clienta_nombre").input("Clienta Pantalla")
        app.text_input(key="clienta_contacto").input("@pantalla")
        self.agregar(app, ("blusa", "M", "disponible", 12000), 2)   # prendas 7 y 22
        self.agregar(app, ("blusa", "L", "en_remate", 6000), 1)     # prenda 10
        self.assertEqual(len(app.session_state["carrito"]), 2)

        # resumen: 2 x 12000 + 6000 = 30000; margen 9000 + 9000 + 3000 = 21000
        valores = {m.label: m.value for m in app.metric}
        self.assertEqual(valores, {"Total a cobrar": "$30.000", "Margen total": "$21.000"})

        pedidos_antes = self.contar("SELECT COUNT(*) FROM Pedido")
        self.confirmar(app)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.error), 0)
        self.assertIn("Clienta Pantalla, 3 prenda(s), total $30.000", app.success[0].value)
        # despues de guardar la casilla se desmarca y el boton queda desactivado
        self.assertFalse(app.checkbox(key="confirmo_venta").value)
        self.assertTrue(self.boton(app, "Confirmar venta").disabled)

        # doble clic: AppTest, como el navegador, no deja tocar el boton desactivado.
        # Se prueba ademas la segunda barrera: aunque se vuelva a marcar la casilla, con el
        # carrito vacio el clic se ignora y no crea otro pedido ni otra clienta.
        self.confirmar(app)
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Pedido"), pedidos_antes + 1)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente WHERE nombre='Clienta Pantalla'"), 1)
        self.assertEqual(self.contar(
            "SELECT COUNT(*) FROM Prenda WHERE id_prenda IN (7, 22, 10) AND estado='vendida'"), 3)

    def test_carrito_no_deja_pasar_del_stock(self):
        app = self.abrir("paginas/registrar_venta.py")
        abrigo = ("abrigo", "M", "disponible", 18000)  # 2 unidades en stock
        app.selectbox(key="producto_venta").select(abrigo).run()
        self.assertEqual(app.number_input(key="cantidad_venta").max, 2)
        self.agregar(app, abrigo, 2)
        # ya no quedan abrigos M para agregar
        opciones = app.selectbox(key="producto_venta").options
        self.assertFalse(any(o.startswith("abrigo M") for o in opciones))

    def test_boton_desactivado_sin_confirmar(self):
        app = self.abrir("paginas/registrar_venta.py")
        self.assertTrue(self.boton(app, "Confirmar venta").disabled)
        app.checkbox(key="confirmo_venta").check().run()
        self.assertFalse(self.boton(app, "Confirmar venta").disabled)

    def test_venta_con_clienta_existente_por_distribuidor(self):
        app = self.abrir("paginas/registrar_venta.py")
        app.text_input(key="buscar_clienta").input("@clienta3").run()
        self.assertEqual(app.selectbox(key="id_clienta").value, 3)
        self.agregar(app, ("vestido", "S", "disponible", 15000), 1)
        app.radio(key="tipo_entrega").set_value("distribuidor").run()
        app.selectbox(key="id_distribuidor").select(2).run()

        clientas_antes = self.contar("SELECT COUNT(*) FROM Cliente")
        self.confirmar(app)
        self.assertEqual(len(app.error), 0)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Cliente"), clientas_antes)
        self.assertEqual(self.contar(
            "SELECT id_cliente || '-' || id_distribuidor FROM Pedido ORDER BY id_pedido DESC LIMIT 1"), "3-2")

    def test_venta_sin_productos_muestra_error(self):
        app = self.abrir("paginas/registrar_venta.py")
        self.confirmar(app)
        self.assertEqual(len(app.exception), 0)
        self.assertIn("al menos un producto", app.error[0].value)

    def test_entregas_marcar_entregado_con_confirmacion(self):
        app = self.abrir("paginas/entregas.py")
        self.assertTrue(app.button(key="entregar_6").disabled)
        app.checkbox(key="confirmo_6").check().run()
        self.assertFalse(app.button(key="entregar_6").disabled)
        app.button(key="entregar_6").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Pedido N° 6", app.success[0].value)
        self.assertEqual(len([b for b in app.button if b.label == "Marcar entregado"]), 1)
        self.assertIsNotNone(self.contar("SELECT fecha_entrega FROM Pedido WHERE id_pedido=6"))
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=6"), "entregada")


class PruebasPantallasEtapa3(PruebaPantalla):
    def test_revisar_ahora_crea_7_y_luego_0(self):
        app = self.abrir("paginas/alertas.py")
        self.boton(app, "Revisar ahora").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.success[0].value, "Se crearon 7 alertas nuevas.")
        self.assertEqual(len([b for b in app.button if b.label == "Poner en remate"]), 7)
        self.boton(app, "Revisar ahora").click().run()
        self.assertEqual(app.success[0].value, "No hay alertas nuevas.")

    def test_umbral_40_y_revisar_crea_3(self):
        app = self.abrir("paginas/alertas.py")
        app.number_input(key="nuevo_umbral").set_value(40)
        self.boton(app, "Guardar umbral").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.success[0].value, "Umbral guardado: 40 días.")
        self.assertEqual(f.obtener_umbral(), 40)
        self.boton(app, "Revisar ahora").click().run()
        self.assertEqual(app.success[0].value, "Se crearon 3 alertas nuevas.")

    def test_poner_en_remate_con_100_por_ciento(self):
        app = self.abrir("paginas/alertas.py")
        self.boton(app, "Revisar ahora").click().run()
        id_alerta = self.contar("SELECT id_alerta FROM AlertaRemate WHERE id_prenda=7 AND estado_alerta='pendiente'")
        boton = app.button(key="remate_" + str(id_alerta))
        self.assertTrue(boton.disabled)  # sin margen no se puede

        app.number_input(key="margen_" + str(id_alerta)).set_value(100).run()
        self.assertIn("$6.000", " ".join(m.value for m in app.markdown))  # vista previa
        app.button(key="remate_" + str(id_alerta)).click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Prenda N° 7 (blusa M) en remate a $6.000", app.success[0].value)
        self.assertEqual(self.contar("SELECT estado FROM Prenda WHERE id_prenda=7"), "en_remate")
        self.assertEqual(len([b for b in app.button if b.label == "Poner en remate"]), 6)


class PruebasPantallasEtapa5(PruebaPantalla):
    def test_tablero(self):
        app = self.abrir("paginas/tablero.py")
        self.assertEqual(len(app.error), 0)
        self.assertIn("Datos de prueba ficticios", app.warning[0].value)
        valores = {m.label: m.value for m in app.metric}
        self.assertEqual(valores["Disponible"], "13")
        self.assertEqual(valores["Ventas (total)"], "$183.000")
        self.assertEqual(valores["Margen (total)"], "$145.000")
        self.assertEqual(valores["Margen bruto"], "79,2 %")
        self.assertEqual(valores["Margen medio por prenda"], "$12.083")
        self.assertEqual(valores["Lotes que alcanzan la meta"], "2 de 3")
        self.assertEqual(valores["Sobre el umbral de 30 días"], "53,8 %")

        tabla = app.dataframe[0].value
        self.assertEqual(list(tabla["Meta"]), ["✅ Alcanzó", "✅ Alcanzó", "⏳ Aún no"])
        self.assertEqual(list(tabla["Veces"]), ["2,83", "2,43", "1,25"])

        # Formula, fuente y meta: en la tabla del desplegable final, no en el cuerpo del tablero
        self.assertEqual(len(app.caption), 2)  # solo "12 prendas vendidas" y "7 de 13 ..."
        self.assertEqual(app.expander[0].label, "ℹ️ Cómo se calculan estos indicadores")
        fichas = app.expander[0].dataframe[0].value
        self.assertEqual(list(fichas.columns), ["KPI", "Fórmula", "Fuente", "Meta", "Responsable"])
        self.assertEqual(set(fichas["Responsable"]), {"Belén"})
        self.assertEqual(len(fichas), 5)
        self.assertEqual(list(fichas["Meta"]).count("Por definir con Belén"), 4)  # K1, K2, K3 y K5
        self.assertIn("≥ 2,0 veces la inversión", fichas["Meta"].iloc[3])

    def test_tablero_sin_ventas(self):
        con = sqlite3.connect(self.ruta)
        con.execute("DELETE FROM DetallePedido")
        con.commit()
        con.close()
        app = self.abrir("paginas/tablero.py")
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Sin ventas registradas.", [i.value for i in app.info])


class PruebasAcceso(unittest.TestCase):
    # RNF-03: sin la clave correcta no se ve nada de la app
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.carpeta.name, "prueba.db")
        crear_base_temporal(self.ruta)
        self.ruta_original = f.ruta_bd
        f.ruta_bd = self.ruta

    def tearDown(self):
        f.ruta_bd = self.ruta_original
        self.carpeta.cleanup()

    def app_sin_sesion(self):
        app = AppTest.from_file(RUTA_APP)
        app.secrets["clave_acceso"] = CLAVE_PRUEBA
        return app.run()

    def entrar(self, app, clave):
        app.text_input(key="clave_ingresada").input(clave)
        [b for b in app.button if b.label == "Entrar"][0].click().run()

    def test_sin_clave_configurada_explica_como_crearla(self):
        # Se pasan secretos SIN clave_acceso: si app.secrets queda vacio, AppTest usaria
        # el secrets.toml real del computador y la prueba dependeria de el.
        app = AppTest.from_file(RUTA_APP)
        app.secrets["otra_cosa"] = "x"
        app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("secrets.toml.example", app.error[0].value)
        self.assertEqual(len(app.text_input), 0)  # ni siquiera el formulario de acceso

    def test_sin_clave_no_se_ve_la_app(self):
        app = self.app_sin_sesion()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.metric), 0)     # la pantalla Inventario no se cargo
        self.assertEqual(len(app.dataframe), 0)
        self.assertFalse([b for b in app.button if b.label == "Cerrar sesión"])

    def test_clave_incorrecta(self):
        app = self.app_sin_sesion()
        self.entrar(app, "otra-clave")
        self.assertEqual(app.error[0].value, "Clave incorrecta.")
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(app.text_input(key="clave_ingresada").value, "")  # se borra lo escrito

    def test_clave_correcta_muestra_la_app_y_cerrar_sesion(self):
        app = self.app_sin_sesion()
        self.entrar(app, CLAVE_PRUEBA)
        self.assertEqual(len(app.exception), 0)
        self.assertGreater(len(app.metric), 0)  # se ve Inventario
        [b for b in app.button if b.label == "Cerrar sesión"][0].click().run()
        self.assertEqual(len(app.metric), 0)
        self.assertEqual(len(app.text_input(key="clave_ingresada").value), 0)


class PruebasPantallasEtapa4(PruebaPantalla):
    def test_publicar_producto_en_remate(self):
        app = self.abrir("paginas/publicar.py")
        publicaciones_antes = self.contar("SELECT COUNT(*) FROM Publicacion")
        app.selectbox(key="producto_publicar").select(("blusa", "L", "en_remate", 6000)).run()
        self.boton(app, "Generar ficha").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("1 unidad(es)", app.success[0].value)
        texto = app.text_area[0].value
        self.assertIn("REMATE", texto)
        self.assertIn("Ahora $6.000", texto)
        self.assertEqual(self.contar("SELECT COUNT(*) FROM Publicacion"), publicaciones_antes + 1)


if __name__ == "__main__":
    unittest.main()
