import sqlite3
import os

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(carpeta, "data", "altafacha.db")

with open(os.path.join(carpeta, "sql", "consultas.sql"), encoding="utf-8") as f:
    texto = f.read()

con = sqlite3.connect(ruta_bd)

for bloque in texto.split(";"):
    lineas = [l for l in bloque.strip().splitlines() if l.strip()]
    if not lineas:
        continue
    titulo = lineas[0] if lineas[0].startswith("--") else "Consulta"
    sql = "\n".join(l for l in lineas if not l.strip().startswith("--"))

    cur = con.execute(sql)
    columnas = [c[0] for c in cur.description]
    filas = cur.fetchall()

    print("\n" + titulo)
    print(" | ".join(columnas))
    for fila in filas:
        print(" | ".join(str(x) for x in fila))
    print("(" + str(len(filas)) + " filas)")

con.close()
