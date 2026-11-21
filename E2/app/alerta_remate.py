# Revision diaria de prendas sin venta (tarea "Evaluar dias sin venta por prenda" del BPMN to-be)
# Si una prenda disponible supera el umbral que ingreso Belén, se genera una alerta de remate.
# Se usa de dos formas:
#   - desde la terminal o ejecutar_alerta.bat:  python alerta_remate.py
#   - desde la app (pantalla Alertas):          generar_alertas(ruta)

import sqlite3
import os

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(carpeta, "data", "altafacha.db")


def generar_alertas(ruta=ruta_bd, mostrar=False):
    # Crea una alerta 'pendiente' por cada prenda disponible que supera el umbral y que
    # no tenga ya una alerta pendiente (por eso correrla dos veces no duplica alertas).
    # ruta: base a usar (los tests pasan una base temporal).
    # mostrar: True imprime el detalle, como cuando se corre desde la terminal.
    # Devuelve las alertas nuevas: [(id_prenda, tipo, talla, dias_sin_venta), ...]
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON")
    try:
        umbral = con.execute("SELECT umbral_dias FROM Configuracion WHERE id_config = 1").fetchone()[0]

        # prendas disponibles sobre el umbral que no tengan ya una alerta pendiente
        # TODO(Belén): los dias se cuentan desde Lote.fecha_recepcion (P3 en ../docs/08-supuestos.md).
        # TODO(Belén): se compara con dias fraccionarios (> umbral), asi que con umbral 30
        #              se alerta el dia 30 y no el 31 (P4).
        prendas = con.execute("""
            SELECT p.id_prenda, p.tipo, p.talla,
                   CAST(julianday('now', 'localtime') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_sin_venta
            FROM Prenda p
            JOIN Lote l ON p.id_lote = l.id_lote
            WHERE p.estado = 'disponible'
              AND julianday('now', 'localtime') - julianday(l.fecha_recepcion) > ?
              AND p.id_prenda NOT IN (
                  SELECT id_prenda FROM AlertaRemate WHERE estado_alerta = 'pendiente'
              )
        """, (umbral,)).fetchall()

        hoy = con.execute("SELECT date('now', 'localtime')").fetchone()[0]
        if mostrar:
            print("Revision del", hoy, "- umbral:", umbral, "dias")

        if len(prendas) == 0:
            if mostrar:
                print("Sin prendas para remate")
        else:
            for id_prenda, tipo, talla, dias in prendas:
                con.execute("""
                    INSERT INTO AlertaRemate (id_prenda, fecha_alerta, dias_sin_venta, estado_alerta)
                    VALUES (?, ?, ?, 'pendiente')
                """, (id_prenda, hoy, dias))
                if mostrar:
                    print("Alerta generada: prenda", id_prenda, "-", tipo, talla, "-", dias, "dias sin venta")
            if mostrar:
                print("Total alertas nuevas:", len(prendas))

        con.commit()
        return prendas
    except Exception:
        con.rollback()  # si falla una alerta no quedan alertas a medias
        raise
    finally:
        con.close()


if __name__ == "__main__":
    generar_alertas(mostrar=True)
