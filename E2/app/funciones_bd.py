# Funciones para usar la base de datos desde la app (Streamlit)
# Ejemplo: from funciones_bd import stock_disponible

import sqlite3
import os
from datetime import datetime

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_bd = os.path.join(carpeta, "data", "altafacha.db")


def conectar():
    con = sqlite3.connect(ruta_bd)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def stock_disponible():
    con = conectar()
    filas = con.execute("""
        SELECT p.id_prenda, p.tipo, p.talla, p.precio_venta, p.precio_remate, p.estado,
               CAST(julianday('now', 'localtime') - julianday(l.fecha_recepcion) AS INTEGER) AS dias_en_stock
        FROM Prenda p JOIN Lote l ON p.id_lote = l.id_lote
        WHERE p.estado IN ('disponible', 'en_remate')
        ORDER BY dias_en_stock DESC
    """).fetchall()
    con.close()
    return filas


def stock_por_producto():
    # Inventario agrupado: un "producto" es la combinacion tipo + talla (ej: vestido rojo, S).
    # Stock = disponible + en_remate (regla R2). Se agrupan TODAS las prendas, asi los
    # productos que ya se vendieron completos aparecen con 0 (sin stock).
    # Devuelve [(tipo, talla, unidades_en_stock, unidades_en_remate), ...]
    con = conectar()
    filas = con.execute("""
        SELECT tipo, talla,
               SUM(estado IN ('disponible', 'en_remate')) AS en_stock,
               SUM(estado = 'en_remate') AS en_remate
        FROM Prenda
        GROUP BY tipo, talla
        ORDER BY tipo, talla
    """).fetchall()
    con.close()
    return filas


def inventario_por_estado():
    # Resumen de inventario (RF-09). Devuelve [(estado, cantidad), ...] en este orden:
    # disponible, en_remate, vendida, entregada. Los estados sin prendas aparecen con 0.
    con = conectar()
    filas = dict(con.execute("SELECT estado, COUNT(*) FROM Prenda GROUP BY estado").fetchall())
    con.close()
    return [(e, filas.get(e, 0)) for e in ("disponible", "en_remate", "vendida", "entregada")]


def listar_proveedores():
    # Para elegir el proveedor al registrar un lote. Devuelve [(id_proveedor, nombre), ...]
    con = conectar()
    filas = con.execute("SELECT id_proveedor, nombre FROM Proveedor ORDER BY nombre").fetchall()
    con.close()
    return filas


def es_entero_positivo(valor):
    # Montos (pesos chilenos) y cantidades: enteros mayores que 0.
    # bool tambien es int en Python (True == 1), por eso se excluye aparte.
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def validar_prenda(prenda):
    # prenda: diccionario con tipo, talla, costo, precio_venta y, opcional, cantidad.
    # Devuelve el texto del error, o None si esta bien. La usa registrar_lote
    # y tambien la pantalla, para avisar apenas se agrega cada prenda.
    if not str(prenda.get("tipo") or "").strip():
        return "Falta el tipo de prenda."
    if not str(prenda.get("talla") or "").strip():
        return "Falta la talla."
    if not es_entero_positivo(prenda.get("costo")):
        return "El costo debe ser un monto mayor que 0."
    if not es_entero_positivo(prenda.get("precio_venta")):
        return "El precio de venta debe ser un monto mayor que 0."
    if not es_entero_positivo(prenda.get("cantidad", 1)):
        return "La cantidad debe ser un número entero mayor que 0."
    return None


# Quita las tildes pero deja la ñ ("Polerón" -> "poleron", "pañuelo" sigue igual)
SIN_TILDES = str.maketrans("áéíóúü", "aeiouu")


def normalizar_texto(texto):
    # Minusculas, sin tildes y sin espacios repetidos: " Vestido  Rojo " -> "vestido rojo"
    return " ".join(texto.lower().translate(SIN_TILDES).split())


def normalizar_prenda(prenda):
    # Asi "Vestido", "vestido" y "VESTIDO" quedan como el mismo tipo y el filtro
    # del inventario los agrupa. La talla va en mayusculas: "s" -> "S", "xl" -> "XL".
    return {
        "tipo": normalizar_texto(prenda["tipo"]),
        "talla": normalizar_texto(prenda["talla"]).upper(),
        "costo": prenda["costo"],
        "precio_venta": prenda["precio_venta"],
        "cantidad": prenda.get("cantidad", 1),
    }


def registrar_lote(proveedor, fecha_recepcion, costo_total, prendas):
    # RF-01 y RF-02. Crea el lote y una ficha (Prenda) por cada prenda, en estado 'disponible'.
    # proveedor: id (int) de un proveedor existente, o nombre (str) de uno nuevo que se crea.
    # fecha_recepcion: texto AAAA-MM-DD. prendas: lista de diccionarios con
    # tipo, talla, costo y precio_venta (por unidad) y, opcional, cantidad (por defecto 1).
    # Si cantidad es 10 se crean 10 fichas iguales: cada unidad se vende una sola vez
    # y tiene su propio estado, por eso no se guarda como una sola fila.
    # Regla R1: cada prenda guarda el costo individual que ingresa Belen; el costo
    # total del lote se guarda aparte y NO se reparte entre las prendas.
    # TODO(equipo): relacion entre la suma de los costos y costo_total pendiente (P1
    # en ../docs/08-supuestos.md). Hoy no se valida.

    # Primero se valida todo, antes de tocar la base
    if not es_entero_positivo(costo_total):
        raise ValueError("El costo total del lote debe ser un monto mayor que 0.")
    if not prendas:
        raise ValueError("El lote debe tener al menos 1 prenda.")
    for numero, prenda in enumerate(prendas, start=1):
        error = validar_prenda(prenda)
        if error:
            raise ValueError("Prenda " + str(numero) + ": " + error)
    try:
        datetime.strptime(fecha_recepcion, "%Y-%m-%d")
    except (TypeError, ValueError):
        raise ValueError("La fecha de recepción debe tener el formato AAAA-MM-DD.")

    proveedor_nuevo = isinstance(proveedor, str)
    if proveedor_nuevo:
        nombre_proveedor = proveedor.strip()
        if not nombre_proveedor:
            raise ValueError("Falta el nombre del proveedor nuevo.")
    elif not isinstance(proveedor, int) or isinstance(proveedor, bool):
        raise ValueError("Proveedor no válido.")

    prendas = [normalizar_prenda(p) for p in prendas]
    total_unidades = sum(p["cantidad"] for p in prendas)

    # Todo en una sola transaccion: si algo falla no queda ni proveedor, ni lote, ni prendas a medias
    con = conectar()
    try:
        if proveedor_nuevo:
            cur = con.execute("INSERT INTO Proveedor (nombre) VALUES (?)", (nombre_proveedor,))
            id_proveedor = cur.lastrowid
        else:
            existe = con.execute("SELECT 1 FROM Proveedor WHERE id_proveedor = ?", (proveedor,)).fetchone()
            if existe is None:
                raise ValueError("El proveedor elegido no existe.")
            id_proveedor = proveedor

        cur = con.execute("""
            INSERT INTO Lote (id_proveedor, fecha_recepcion, costo_total, cantidad_prendas)
            VALUES (?, ?, ?, ?)
        """, (id_proveedor, fecha_recepcion, costo_total, total_unidades))
        id_lote = cur.lastrowid

        for prenda in prendas:
            for _ in range(prenda["cantidad"]):
                con.execute("""
                    INSERT INTO Prenda (id_lote, tipo, talla, costo, precio_venta, estado)
                    VALUES (?, ?, ?, ?, ?, 'disponible')
                """, (id_lote, prenda["tipo"], prenda["talla"],
                      prenda["costo"], prenda["precio_venta"]))

        con.commit()
        return id_lote
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def obtener_lote(id_lote):
    # Datos del lote tal como quedaron en la base, para el resumen despues de guardar.
    # Devuelve (id_lote, proveedor, fecha_recepcion, costo_total, cantidad_prendas)
    con = conectar()
    fila = con.execute("""
        SELECT l.id_lote, pr.nombre, l.fecha_recepcion, l.costo_total, l.cantidad_prendas
        FROM Lote l JOIN Proveedor pr ON l.id_proveedor = pr.id_proveedor
        WHERE l.id_lote = ?
    """, (id_lote,)).fetchone()
    con.close()
    return fila


def prendas_de_lote(id_lote):
    # Fichas de las prendas de un lote: [(id_prenda, tipo, talla, costo, precio_venta, estado), ...]
    con = conectar()
    filas = con.execute("""
        SELECT id_prenda, tipo, talla, costo, precio_venta, estado
        FROM Prenda WHERE id_lote = ? ORDER BY id_prenda
    """, (id_lote,)).fetchall()
    con.close()
    return filas


def obtener_umbral():
    con = conectar()
    umbral = con.execute("SELECT umbral_dias FROM Configuracion WHERE id_config = 1").fetchone()[0]
    con.close()
    return umbral


def actualizar_umbral(dias):
    # RF-10. El umbral son dias enteros mayores que 0.
    if not es_entero_positivo(dias):
        raise ValueError("El umbral debe ser un número entero de días mayor que 0.")
    con = conectar()
    con.execute("UPDATE Configuracion SET umbral_dias = ? WHERE id_config = 1", (dias,))
    con.commit()
    con.close()


def alertas_pendientes():
    # Solo alertas cuya prenda sigue disponible: si Belen la vendio antes de atender la
    # alerta, ya no tiene sentido rematarla y no se muestra (la alerta queda 'pendiente' en la base).
    con = conectar()
    filas = con.execute("""
        SELECT a.id_alerta, a.id_prenda, p.tipo, p.talla, p.costo, p.precio_venta,
               a.dias_sin_venta, a.fecha_alerta
        FROM AlertaRemate a JOIN Prenda p ON a.id_prenda = p.id_prenda
        WHERE a.estado_alerta = 'pendiente' AND p.estado = 'disponible'
        ORDER BY a.dias_sin_venta DESC
    """).fetchall()
    con.close()
    return filas


def calcular_precio_remate(costo, margen):
    # margen sobre el costo, ej: 1.0 = 100% -> costo 3000 queda en 6000.
    # La usan atender_alerta y la vista previa de la pantalla, asi muestran el mismo precio.
    return round(costo * (1 + margen))


def atender_alerta(id_alerta, margen):
    # Belen define el margen de remate: la prenda pasa a 'en_remate' con su precio de remate
    # y la alerta queda 'atendida'. Todo en una transaccion.
    # Margen >= 0: el precio de remate nunca queda bajo el costo (ver L2 en
    # ../docs/Limitaciones_en_desarrollo.md).
    if isinstance(margen, bool) or not isinstance(margen, (int, float)) or margen < 0:
        raise ValueError("El margen debe ser un número mayor o igual a 0 %.")

    con = conectar()
    try:
        fila = con.execute("""
            SELECT p.id_prenda, p.costo, p.estado, a.estado_alerta FROM AlertaRemate a
            JOIN Prenda p ON a.id_prenda = p.id_prenda
            WHERE a.id_alerta = ?
        """, (id_alerta,)).fetchone()
        if fila is None:
            raise ValueError("La alerta no existe.")
        id_prenda, costo, estado_prenda, estado_alerta = fila
        if estado_alerta != "pendiente":
            raise ValueError("Esta alerta ya fue atendida.")
        # Si la prenda se vendio despues de la alerta, no se puede volver a poner en remate:
        # quedaria otra vez en stock y se podria vender dos veces.
        if estado_prenda != "disponible":
            raise ValueError("La prenda N° " + str(id_prenda) + " ya no está disponible (está " +
                             estado_prenda + ").")

        precio_remate = calcular_precio_remate(costo, margen)
        con.execute("UPDATE Prenda SET precio_remate = ?, estado = 'en_remate' WHERE id_prenda = ?",
                    (precio_remate, id_prenda))
        con.execute("UPDATE AlertaRemate SET margen_remate = ?, estado_alerta = 'atendida' WHERE id_alerta = ?",
                    (margen, id_alerta))
        con.commit()
        return precio_remate
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def buscar_clientas(texto=""):
    # Para que Belen ELIJA una clienta existente: busca el texto en el nombre o el contacto.
    # LIKE en SQLite no distingue mayusculas (en letras sin tilde). Con texto vacio trae las primeras.
    # No se asocia nada automaticamente: el contacto no es unico (regla R3).
    # Devuelve [(id_cliente, nombre, contacto, comuna), ...], maximo 20.
    patron = "%" + texto.strip() + "%"
    con = conectar()
    filas = con.execute("""
        SELECT id_cliente, nombre, contacto, comuna FROM Cliente
        WHERE nombre LIKE ? OR contacto LIKE ?
        ORDER BY nombre, id_cliente
        LIMIT 20
    """, (patron, patron)).fetchall()
    con.close()
    return filas


def listar_distribuidores():
    # Devuelve [(id_distribuidor, nombre), ...]
    con = conectar()
    filas = con.execute("SELECT id_distribuidor, nombre FROM Distribuidor ORDER BY nombre").fetchall()
    con.close()
    return filas


def prendas_para_venta():
    # Prendas que se pueden vender (disponible o en_remate) con el precio que se cobraria:
    # el de remate si esta en remate, si no el de venta (regla R4, igual que registrar_venta).
    # Devuelve [(id_prenda, tipo, talla, estado, precio_a_cobrar, margen), ...]
    con = conectar()
    filas = con.execute("""
        SELECT id_prenda, tipo, talla, estado, precio_a_cobrar, precio_a_cobrar - costo AS margen
        FROM (
            SELECT id_prenda, tipo, talla, estado, costo,
                   CASE WHEN estado = 'en_remate' THEN precio_remate ELSE precio_venta END AS precio_a_cobrar
            FROM Prenda
            WHERE estado IN ('disponible', 'en_remate')
        )
        ORDER BY tipo, talla, id_prenda
    """).fetchall()
    con.close()
    return filas


def productos_para_venta():
    # Para vender por producto y cantidad en vez de por ID.
    # Un producto para vender = tipo + talla + precio que se cobra. Las unidades en remate
    # quedan en una linea aparte porque se cobran a otro precio (regla R4).
    # Devuelve [(tipo, talla, estado, precio_a_cobrar, unidades), ...]
    con = conectar()
    filas = con.execute("""
        SELECT tipo, talla, estado, precio_a_cobrar, COUNT(*) AS unidades
        FROM (
            SELECT tipo, talla, estado,
                   CASE WHEN estado = 'en_remate' THEN precio_remate ELSE precio_venta END AS precio_a_cobrar
            FROM Prenda
            WHERE estado IN ('disponible', 'en_remate')
        )
        GROUP BY tipo, talla, estado, precio_a_cobrar
        ORDER BY tipo, talla, estado, precio_a_cobrar
    """).fetchall()
    con.close()
    return filas


def elegir_prendas(productos):
    # Convierte "2 vestido rojo S" en los id_prenda concretos que se van a vender.
    # productos: lista de diccionarios con tipo, talla, estado, precio y cantidad.
    # Se eligen las unidades MAS ANTIGUAS (lote recibido antes): asi sale primero lo que
    # lleva mas tiempo en stock. Si se piden mas unidades que las que hay, da error.
    # Solo lee la base; la venta la guarda registrar_venta().
    if not productos:
        raise ValueError("Elige al menos un producto.")

    # Si un mismo producto viene dos veces, se suman las cantidades
    pedidos = {}
    for producto in productos:
        if not es_entero_positivo(producto.get("cantidad")):
            raise ValueError("La cantidad debe ser un número entero mayor que 0.")
        if producto.get("estado") not in ("disponible", "en_remate"):
            raise ValueError("Producto no válido.")
        clave = (producto["tipo"], producto["talla"], producto["estado"], producto["precio"])
        pedidos[clave] = pedidos.get(clave, 0) + producto["cantidad"]

    ids = []
    con = conectar()
    try:
        for (tipo, talla, estado, precio), cantidad in pedidos.items():
            filas = con.execute("""
                SELECT p.id_prenda
                FROM Prenda p JOIN Lote l ON p.id_lote = l.id_lote
                WHERE p.tipo = ? AND p.talla = ? AND p.estado = ?
                  AND (CASE WHEN p.estado = 'en_remate' THEN p.precio_remate ELSE p.precio_venta END) = ?
                ORDER BY l.fecha_recepcion, p.id_prenda
                LIMIT ?
            """, (tipo, talla, estado, precio, cantidad)).fetchall()
            if len(filas) < cantidad:
                nombre = tipo + " talla " + talla + (" (remate)" if estado == "en_remate" else "")
                raise ValueError("Solo quedan " + str(len(filas)) + " unidad(es) de " + nombre + ".")
            ids += [fila[0] for fila in filas]
    finally:
        con.close()
    return ids


def registrar_venta_por_producto(clienta, productos, tipo_entrega, id_distribuidor=None):
    # Venta por producto y cantidad: elige las unidades y usa registrar_venta(), que hace
    # la transaccion, cobra el precio (R4), calcula el margen y crea la clienta nueva (R3).
    # registrar_venta vuelve a revisar que cada prenda siga disponible, asi que una prenda
    # nunca se vende dos veces aunque algo cambie entre los dos pasos.
    ids = elegir_prendas(productos)
    return registrar_venta(clienta, ids, tipo_entrega, id_distribuidor)


def registrar_venta(clienta, prendas, tipo_entrega, id_distribuidor=None):
    # RF-03, RF-04, RF-05. Hace los 3 pasos del BPMN to-be: registrar venta, descontar
    # inventario y calcular margen.
    # clienta: id_cliente (int) de una clienta existente, o diccionario
    # {"nombre", "contacto", "comuna"} de una clienta nueva. La clienta nueva se crea en la
    # MISMA transaccion que la venta: si la venta falla, la clienta tampoco queda (regla R3).
    # prendas: lista de id_prenda. Si la prenda esta en remate se cobra el precio de remate (R4).

    # Primero se valida todo, antes de tocar la base
    if not prendas:
        raise ValueError("Elige al menos una prenda.")
    if len(set(prendas)) != len(prendas):
        raise ValueError("Hay una prenda repetida en la venta.")
    if tipo_entrega not in ("propia", "distribuidor"):
        raise ValueError("Tipo de entrega no válido.")
    if tipo_entrega == "propia":
        id_distribuidor = None  # si Belen entrega en persona no hay distribuidor
    elif id_distribuidor is None:
        raise ValueError("Elige el distribuidor que hará la entrega.")

    clienta_nueva = isinstance(clienta, dict)
    if clienta_nueva:
        nombre = str(clienta.get("nombre") or "").strip()
        if not nombre:
            raise ValueError("Falta el nombre de la clienta nueva.")
        # Ley 21.719: solo nombre, contacto y comuna. Contacto y comuna son opcionales.
        contacto = str(clienta.get("contacto") or "").strip() or None
        comuna = str(clienta.get("comuna") or "").strip() or None
    elif not isinstance(clienta, int) or isinstance(clienta, bool):
        raise ValueError("Clienta no válida.")

    con = conectar()
    try:
        if clienta_nueva:
            cur = con.execute("INSERT INTO Cliente (nombre, contacto, comuna) VALUES (?, ?, ?)",
                              (nombre, contacto, comuna))
            id_cliente = cur.lastrowid
        else:
            if con.execute("SELECT 1 FROM Cliente WHERE id_cliente = ?", (clienta,)).fetchone() is None:
                raise ValueError("La clienta elegida no existe.")
            id_cliente = clienta

        if id_distribuidor is not None:
            existe = con.execute("SELECT 1 FROM Distribuidor WHERE id_distribuidor = ?",
                                 (id_distribuidor,)).fetchone()
            if existe is None:
                raise ValueError("El distribuidor elegido no existe.")

        cur = con.execute("""
            INSERT INTO Pedido (id_cliente, id_distribuidor, fecha_venta, tipo_entrega)
            VALUES (?, ?, date('now', 'localtime'), ?)
        """, (id_cliente, id_distribuidor, tipo_entrega))
        id_pedido = cur.lastrowid

        for id_prenda in prendas:
            fila = con.execute("SELECT costo, precio_venta, precio_remate, estado FROM Prenda WHERE id_prenda = ?",
                               (id_prenda,)).fetchone()
            if fila is None:
                raise ValueError("La prenda N° " + str(id_prenda) + " no existe.")
            costo, precio_venta, precio_remate, estado = fila
            if estado not in ("disponible", "en_remate"):
                raise ValueError("La prenda N° " + str(id_prenda) + " ya no está disponible (está " + estado + ").")

            precio_final = precio_remate if estado == "en_remate" else precio_venta
            con.execute("INSERT INTO DetallePedido VALUES (?, ?, ?, ?)",
                        (id_pedido, id_prenda, precio_final, precio_final - costo))
            con.execute("UPDATE Prenda SET estado = 'vendida' WHERE id_prenda = ?", (id_prenda,))

        con.commit()
        return id_pedido
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def unidades_de_producto(con, producto):
    # Unidades de un producto (tipo + talla + estado + precio que se cobra), igual que lo
    # agrupa productos_para_venta(). Las mas antiguas primero.
    # Devuelve [(id_prenda, precio_venta, ultima_fecha_publicacion o None), ...]
    return con.execute("""
        SELECT p.id_prenda, p.precio_venta,
               (SELECT MAX(pu.fecha_publicacion) FROM Publicacion pu WHERE pu.id_prenda = p.id_prenda)
        FROM Prenda p JOIN Lote l ON p.id_lote = l.id_lote
        WHERE p.tipo = ? AND p.talla = ? AND p.estado = ?
          AND (CASE WHEN p.estado = 'en_remate' THEN p.precio_remate ELSE p.precio_venta END) = ?
        ORDER BY l.fecha_recepcion, p.id_prenda
    """, (producto["tipo"], producto["talla"], producto["estado"], producto["precio"])).fetchall()


def texto_pesos(monto):
    # 12000 -> "$12.000". Mismo formato que app/formato.py; se repite aqui porque la capa
    # de datos no debe depender de la carpeta de la interfaz.
    return "$" + f"{monto:,}".replace(",", ".")


def generar_ficha_publicacion(producto):
    # RF-06. Arma el texto para pegar en Instagram y guarda una fila en Publicacion por
    # cada unidad del producto (asi cada prenda tiene su historial de publicacion).
    # Una prenda puede tener varias publicaciones: cada llamada agrega filas nuevas.
    # producto: diccionario con tipo, talla, estado y precio (como en productos_para_venta).
    # Devuelve (texto, unidades_publicadas).
    if producto.get("estado") not in ("disponible", "en_remate"):
        raise ValueError("Solo se pueden publicar prendas disponibles o en remate.")

    con = conectar()
    try:
        unidades = unidades_de_producto(con, producto)
        if not unidades:
            raise ValueError("No quedan unidades de este producto para publicar.")

        # El tipo se guarda en minusculas y sin tildes: aqui solo se pone la primera en mayuscula
        nombre = producto["tipo"].capitalize() + " · Talla " + producto["talla"]
        if producto["estado"] == "en_remate":
            # Precio "antes": el de venta. Si las unidades tuvieran precios de venta
            # distintos se muestra el mayor.
            antes = max(precio_venta for _, precio_venta, _ in unidades)
            lineas = ["🔥 ¡REMATE! 🔥",
                      "✨ " + nombre + " ✨",
                      "💰 Antes " + texto_pesos(antes) + " → Ahora " + texto_pesos(producto["precio"])]
        else:
            lineas = ["✨ " + nombre + " ✨",
                      "💰 " + texto_pesos(producto["precio"])]
        lineas.append("📩 Escríbenos por DM para comprarla")
        texto = "\n".join(lineas)

        for id_prenda, _, _ in unidades:
            con.execute("""
                INSERT INTO Publicacion (id_prenda, fecha_publicacion, descripcion, foto)
                VALUES (?, date('now', 'localtime'), ?, NULL)
            """, (id_prenda, texto))
        con.commit()
        return texto, len(unidades)
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def ultima_publicacion(producto):
    # Fecha de la ultima publicacion de alguna unidad del producto, o None si nunca se publico
    con = conectar()
    fechas = [fecha for _, _, fecha in unidades_de_producto(con, producto) if fecha]
    con.close()
    return max(fechas) if fechas else None  # AAAA-MM-DD se puede comparar como texto


def obtener_pedido(id_pedido):
    # Resumen de un pedido tal como quedo en la base, para confirmar la venta.
    # Devuelve (id_pedido, nombre_clienta, fecha_venta, cantidad_prendas, total, margen_total)
    con = conectar()
    fila = con.execute("""
        SELECT pe.id_pedido, c.nombre, pe.fecha_venta,
               COUNT(dp.id_prenda), SUM(dp.precio_final), SUM(dp.margen)
        FROM Pedido pe
        JOIN Cliente c ON pe.id_cliente = c.id_cliente
        JOIN DetallePedido dp ON dp.id_pedido = pe.id_pedido
        WHERE pe.id_pedido = ?
        GROUP BY pe.id_pedido
    """, (id_pedido,)).fetchone()
    con.close()
    return fila


def pedidos_pendientes_entrega():
    # Pedidos sin fecha de entrega (RF-08), los mas antiguos primero.
    # Devuelve [(id_pedido, fecha_venta, clienta, contacto, tipo_entrega, distribuidor,
    #            prendas, total, dias_desde_venta), ...]
    # distribuidor es None si la entrega es propia.
    con = conectar()
    filas = con.execute("""
        SELECT pe.id_pedido, pe.fecha_venta, c.nombre, c.contacto, pe.tipo_entrega, d.nombre,
               GROUP_CONCAT(pr.tipo || ' ' || pr.talla, ', ') AS prendas,
               SUM(dp.precio_final) AS total,
               CAST(julianday('now', 'localtime') - julianday(pe.fecha_venta) AS INTEGER) AS dias
        FROM Pedido pe
        JOIN Cliente c ON pe.id_cliente = c.id_cliente
        LEFT JOIN Distribuidor d ON pe.id_distribuidor = d.id_distribuidor
        JOIN DetallePedido dp ON dp.id_pedido = pe.id_pedido
        JOIN Prenda pr ON dp.id_prenda = pr.id_prenda
        WHERE pe.fecha_entrega IS NULL
        GROUP BY pe.id_pedido
        ORDER BY pe.fecha_venta, pe.id_pedido
    """).fetchall()
    con.close()
    return filas


def marcar_entregado(id_pedido):
    con = conectar()
    con.execute("UPDATE Pedido SET fecha_entrega = date('now', 'localtime') WHERE id_pedido = ?", (id_pedido,))
    con.execute("""
        UPDATE Prenda SET estado = 'entregada'
        WHERE id_prenda IN (SELECT id_prenda FROM DetallePedido WHERE id_pedido = ?)
    """, (id_pedido,))
    con.commit()
    con.close()
