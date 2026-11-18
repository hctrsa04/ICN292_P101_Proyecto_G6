# Revision diaria de prendas sin venta (tarea "Evaluar dias sin venta por prenda" del BPMN to-be)
# Si una prenda disponible supera el umbral que ingreso Belén, se genera una alerta de remate.

import sqlite3
import os

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(carpeta, "data", "altafacha.db")

con = sqlite3.connect(ruta_bd)
con.execute("PRAGMA foreign_keys = ON")

umbral = con.execute("SELECT umbral_dias FROM Configuracion WHERE id_config = 1").fetchone()[0]

# prendas disponibles sobre el umbral que no tengan ya una alerta pendiente
prendas = con.execute("""
    SELECT p.id_prenda, p.tipo, p.talla,
           CAST(julianday('now') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_sin_venta
    FROM Prenda p
    JOIN Lote l ON p.id_lote = l.id_lote
    WHERE p.estado = 'disponible'
      AND julianday('now') - julianday(l.fecha_recepcion) > ?
      AND p.id_prenda NOT IN (
          SELECT id_prenda FROM AlertaRemate WHERE estado_alerta = 'pendiente'
      )
""", (umbral,)).fetchall()

hoy = con.execute("SELECT date('now')").fetchone()[0]
print("Revision del", hoy, "- umbral:", umbral, "dias")

if len(prendas) == 0:
    print("Sin prendas para remate")
else:
    for id_prenda, tipo, talla, dias in prendas:
        con.execute("""
            INSERT INTO AlertaRemate (id_prenda, fecha_alerta, dias_sin_venta, estado_alerta)
            VALUES (?, ?, ?, 'pendiente')
        """, (id_prenda, hoy, dias))
        print("Alerta generada: prenda", id_prenda, "-", tipo, talla, "-", dias, "dias sin venta")
    print("Total alertas nuevas:", len(prendas))

con.commit()
con.close()
