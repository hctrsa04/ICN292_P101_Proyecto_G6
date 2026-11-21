# Mide cuanto tarda cada pantalla y las acciones principales (RNF-04: menos de 3 segundos).
# Usa bases TEMPORALES (nunca toca data/altafacha.db):
#   - base de prueba: schema.sql + datos_prueba.sql (26 prendas)
#   - base grande: la de prueba + 30 lotes de 100 prendas y 1.000 ventas, creadas con
#     las mismas funciones de la app (registrar_lote / registrar_venta)
# Mide el tiempo del servidor (consultas + armar la pantalla) con AppTest de Streamlit;
# no incluye el dibujo en el navegador ni la red.
#
# Ejecutar desde la carpeta raiz del proyecto:  python medir_tiempos.py

import datetime
import os
import sqlite3
import statistics
import sys
import tempfile
import time

from streamlit.testing.v1 import AppTest

carpeta = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, carpeta)

import alerta_remate  # noqa: E402
import funciones_bd  # noqa: E402

RUTA_APP = os.path.join(carpeta, "app", "main.py")
PAGINAS = ["inventario", "registrar_lote", "registrar_venta", "entregas", "alertas", "publicar", "tablero"]
REPETICIONES = 3
LIMITE = 3.0  # segundos (RNF-04)

TIPOS = ["vestido", "blusa", "falda", "abrigo", "chaqueta", "polera", "pantalon", "poleron"]
TALLAS = ["XS", "S", "M", "L", "XL"]


def crear_base(ruta):
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON")
    for archivo in ("schema.sql", "datos_prueba.sql"):
        with open(os.path.join(carpeta, "sql", archivo), encoding="utf-8") as fh:
            con.executescript(fh.read())
    con.commit()
    con.close()


def agrandar_base():
    # 30 lotes de 100 prendas (fechas de 0 a 87 dias atras) y 1.000 ventas de 1 prenda.
    # Todo con datos ficticios y con las funciones de la app.
    hoy = datetime.date.today()
    for numero_lote in range(30):
        fecha = (hoy - datetime.timedelta(days=numero_lote * 3)).isoformat()
        prendas = [{"tipo": TIPOS[i % len(TIPOS)], "talla": TALLAS[i % len(TALLAS)],
                    "costo": 2000 + 500 * (i % 4), "precio_venta": 10000 + 1000 * (i % 6)}
                   for i in range(100)]
        funciones_bd.registrar_lote(1 + numero_lote % 2, fecha, 300000, prendas)
    disponibles = [fila[0] for fila in funciones_bd.prendas_para_venta()]
    for i, id_prenda in enumerate(disponibles[:1000]):
        funciones_bd.registrar_venta(1 + i % 4, [id_prenda], "propia")
    # Alertas antes de medir, para que la pantalla Alertas tenga muchas tarjetas
    alerta_remate.generar_alertas(funciones_bd.ruta_bd)


def medir_pantalla(pagina):
    tiempos = []
    for _ in range(REPETICIONES):
        app = AppTest.from_file(RUTA_APP, default_timeout=30)
        app.secrets["clave_acceso"] = "clave-de-medicion"
        app.session_state["autenticada"] = True
        app.run()
        inicio = time.perf_counter()
        app.switch_page("paginas/" + pagina + ".py").run()
        tiempos.append(time.perf_counter() - inicio)
        if app.exception:
            raise RuntimeError("La pantalla " + pagina + " fallo: " + str(app.exception[0].value))
    return statistics.median(tiempos), max(tiempos)


def medir_accion(nombre, funcion):
    inicio = time.perf_counter()
    funcion()
    return nombre, time.perf_counter() - inicio


def medir_acciones():
    producto = funciones_bd.productos_para_venta()[0]
    venta = [{"tipo": producto[0], "talla": producto[1], "estado": producto[2],
              "precio": producto[3], "cantidad": 1}]
    lote = [{"tipo": "vestido", "talla": "M", "costo": 3000, "precio_venta": 15000, "cantidad": 10}]
    return [
        medir_accion("Registrar venta (1 producto)",
                     lambda: funciones_bd.registrar_venta_por_producto(1, venta, "propia")),
        medir_accion("Registrar lote (10 unidades)",
                     lambda: funciones_bd.registrar_lote(1, datetime.date.today().isoformat(), 30000, lote)),
        medir_accion("Revisar alertas (generar_alertas)",
                     lambda: alerta_remate.generar_alertas(funciones_bd.ruta_bd)),
    ]


def informe(titulo):
    con = sqlite3.connect(funciones_bd.ruta_bd)
    prendas, ventas, pendientes, alertas = con.execute("""
        SELECT (SELECT COUNT(*) FROM Prenda), (SELECT COUNT(*) FROM DetallePedido),
               (SELECT COUNT(*) FROM Pedido WHERE fecha_entrega IS NULL),
               (SELECT COUNT(*) FROM AlertaRemate WHERE estado_alerta = 'pendiente')
    """).fetchone()
    con.close()
    print("\n" + titulo + " (" + str(prendas) + " prendas, " + str(ventas) + " vendidas, " +
          str(pendientes) + " pedidos por entregar, " + str(alertas) + " alertas pendientes)")
    print("  Pantalla           mediana   maximo   < 3 s")
    peor = 0
    for pagina in PAGINAS:
        mediana, maximo = medir_pantalla(pagina)
        peor = max(peor, maximo)
        print("  " + pagina.ljust(18) + f"{mediana:6.2f} s {maximo:6.2f} s   " +
              ("si" if maximo < LIMITE else "NO"))
    print("  Accion" + " " * 30 + "tiempo   < 3 s")
    for nombre, segundos in medir_acciones():
        peor = max(peor, segundos)
        print("  " + nombre.ljust(36) + f"{segundos:6.2f} s   " + ("si" if segundos < LIMITE else "NO"))
    return peor


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temporal:
        funciones_bd.ruta_bd = os.path.join(temporal, "medicion.db")
        crear_base(funciones_bd.ruta_bd)
        peor_prueba = informe("Base de prueba")

        crear_base(funciones_bd.ruta_bd + ".grande")
        funciones_bd.ruta_bd = funciones_bd.ruta_bd + ".grande"
        print("\nCreando base grande (puede tardar unos segundos)...")
        agrandar_base()
        peor_grande = informe("Base grande")

    print("\nPeor tiempo: " + f"{max(peor_prueba, peor_grande):.2f}" + " s (objetivo RNF-04: < 3 s)")
