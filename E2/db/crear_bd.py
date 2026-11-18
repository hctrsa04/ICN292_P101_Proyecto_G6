import sqlite3
import os

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(carpeta, "data", "altafacha.db")

os.makedirs(os.path.join(carpeta, "data"), exist_ok=True)

if os.path.exists(ruta_bd):
    os.remove(ruta_bd)

con = sqlite3.connect(ruta_bd)
con.execute("PRAGMA foreign_keys = ON")

for archivo in ["schema.sql", "datos_prueba.sql"]:
    with open(os.path.join(carpeta, "sql", archivo), encoding="utf-8") as f:
        con.executescript(f.read())
    print("Ejecutado:", archivo)

con.commit()
con.close()
print("Base de datos creada en", ruta_bd)
