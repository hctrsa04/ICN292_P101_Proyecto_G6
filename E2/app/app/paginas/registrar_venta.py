# Pantalla "Registrar venta" (RF-03, RF-04, RF-05)
# Paso 1: clienta. Paso 2: productos y unidades (carrito). Paso 3: entrega.
# Paso 4: resumen, confirmar y guardar.

import sqlite3

import pandas as pd
import streamlit as st

import funciones_bd
from formato import pesos

CLIENTA_EXISTENTE = "Clienta existente"
CLIENTA_NUEVA = "Clienta nueva"
NOMBRES_ENTREGA = {"propia": "Entrega propia", "distribuidor": "Por distribuidor"}

# El carrito guarda los productos elegidos hasta confirmar la venta
if "carrito" not in st.session_state:
    st.session_state.carrito = []


def clave(producto):
    # Un producto para vender = tipo + talla + estado + precio (ver productos_para_venta)
    return (producto["tipo"], producto["talla"], producto["estado"], producto["precio"])


def nombre_producto(tipo, talla, estado, precio):
    texto = tipo + " " + talla + " · " + pesos(precio)
    if estado == "en_remate":
        texto += " (remate)"
    return texto


def agregar_al_carrito(disponibles):
    # disponibles: {clave: unidades que quedan sin contar el carrito}
    estado = st.session_state
    estado.pop("ultimo_pedido", None)  # empieza otra venta: se borra el aviso de la anterior
    producto = estado.get("producto_venta")
    cantidad = estado.get("cantidad_venta")
    if producto is None:
        estado.error_carrito = "Elige un producto."
        return
    if not cantidad or cantidad > disponibles[producto]:
        estado.error_carrito = "Solo quedan " + str(disponibles[producto]) + " unidad(es) de ese producto."
        return
    tipo, talla, estado_prenda, precio = producto
    for item in estado.carrito:
        if clave(item) == producto:  # si ya estaba, se suman las unidades
            item["cantidad"] += cantidad
            break
    else:
        estado.carrito.append({"tipo": tipo, "talla": talla, "estado": estado_prenda,
                               "precio": precio, "cantidad": cantidad})
    estado.cantidad_venta = 1


def quitar_ultimo():
    st.session_state.carrito.pop()


def reiniciar_cantidad():
    # Al cambiar de producto la cantidad vuelve a 1, para no pasar el maximo del nuevo producto
    st.session_state.cantidad_venta = 1


def confirmar_venta():
    # Callback del boton: corre antes de redibujar la pantalla, asi se pueden limpiar los campos.
    estado = st.session_state

    # Doble clic: el primer clic ya guardo la venta y vacio el carrito; el segundo se ignora.
    # Ademas, registrar_venta rechaza prendas que ya estan vendidas.
    if not estado.carrito and "ultimo_pedido" in estado:
        return

    if estado.tipo_clienta == CLIENTA_NUEVA:
        clienta = {
            "nombre": estado.get("clienta_nombre", ""),
            "contacto": estado.get("clienta_contacto", ""),
            "comuna": estado.get("clienta_comuna", ""),
        }
    else:
        clienta = estado.get("id_clienta")
        if clienta is None:
            estado.error_venta = "Elige una clienta."
            return

    id_distribuidor = estado.get("id_distribuidor") if estado.tipo_entrega == "distribuidor" else None
    try:
        id_pedido = funciones_bd.registrar_venta_por_producto(clienta, estado.carrito,
                                                              estado.tipo_entrega, id_distribuidor)
    except ValueError as error:
        estado.error_venta = str(error)
        return
    except sqlite3.Error:
        estado.error_venta = "No se pudo guardar la venta y no se guardó nada. Intenta de nuevo."
        return

    estado.ultimo_pedido = id_pedido
    estado.carrito = []
    estado.confirmo_venta = False
    estado.clienta_nombre = ""
    estado.clienta_contacto = ""
    estado.clienta_comuna = ""


st.header("Registrar venta")

# --- Paso 1: clienta ---
st.subheader("1. Clienta")
st.radio("¿Quién compra?", [CLIENTA_EXISTENTE, CLIENTA_NUEVA], horizontal=True, key="tipo_clienta")

if st.session_state.tipo_clienta == CLIENTA_EXISTENTE:
    st.text_input("Buscar por nombre o contacto", placeholder="Ej: Camila o @camila",
                  key="buscar_clienta")
    resultados = funciones_bd.buscar_clientas(st.session_state.buscar_clienta)
    if not resultados:
        st.warning("No se encontraron clientas. Prueba otra búsqueda o elige \"Clienta nueva\".")
    else:
        # Se muestra el N° porque el contacto puede repetirse entre clientas (regla R3)
        textos = {}
        for id_cliente, nombre, contacto, comuna in resultados:
            textos[id_cliente] = " · ".join(x for x in (nombre, contacto, comuna) if x) + \
                " (N° " + str(id_cliente) + ")"
        st.selectbox("Clienta", list(textos), format_func=textos.get, key="id_clienta")
else:
    st.text_input("Nombre", key="clienta_nombre")
    st.text_input("Contacto (Instagram o teléfono, opcional)", key="clienta_contacto")
    st.text_input("Comuna (opcional)", key="clienta_comuna")
    st.caption("Solo se guardan nombre, contacto y comuna (Ley 21.719).")

# --- Paso 2: productos y unidades ---
st.subheader("2. Productos")

# Unidades que quedan de cada producto, descontando lo que ya esta en el carrito
en_carrito = {}
for item in st.session_state.carrito:
    en_carrito[clave(item)] = en_carrito.get(clave(item), 0) + item["cantidad"]
disponibles = {}
for tipo, talla, estado_prenda, precio, unidades in funciones_bd.productos_para_venta():
    restantes = unidades - en_carrito.get((tipo, talla, estado_prenda, precio), 0)
    if restantes > 0:
        disponibles[(tipo, talla, estado_prenda, precio)] = restantes

if not disponibles:
    st.info("No quedan productos disponibles para agregar.")
else:
    st.selectbox(
        "Producto (escribe para buscar)",
        list(disponibles),
        format_func=lambda p: nombre_producto(*p) + " · " + str(disponibles[p]) + " disp.",
        key="producto_venta",
        on_change=reiniciar_cantidad,
    )
    maximo = disponibles[st.session_state.producto_venta]
    # Sin value=: parte en el minimo (1) y los callbacks la reinician a 1
    st.number_input("Unidades (máximo " + str(maximo) + ")", min_value=1, max_value=maximo,
                    step=1, key="cantidad_venta")
    st.button("Agregar a la venta", on_click=agregar_al_carrito, args=(disponibles,), width="stretch")

if "error_carrito" in st.session_state:
    st.error(st.session_state.pop("error_carrito"))

carrito = st.session_state.carrito
if carrito:
    lista = pd.DataFrame(
        [(nombre_producto(i["tipo"], i["talla"], i["estado"], i["precio"]), i["cantidad"],
          i["precio"] * i["cantidad"]) for i in carrito],
        columns=["Producto", "Unidades", "Subtotal"],
    )
    st.dataframe(lista, hide_index=True, width="stretch",
                 column_config={"Subtotal": st.column_config.NumberColumn(format="$%d")})
    st.button("Quitar último producto", on_click=quitar_ultimo, width="stretch")

# --- Paso 3: entrega ---
st.subheader("3. Entrega")
st.radio("¿Cómo se entrega?", list(NOMBRES_ENTREGA), format_func=NOMBRES_ENTREGA.get,
         horizontal=True, key="tipo_entrega")
if st.session_state.tipo_entrega == "distribuidor":
    distribuidores = dict(funciones_bd.listar_distribuidores())
    if not distribuidores:
        st.warning("No hay distribuidores registrados.")
    else:
        st.selectbox("Distribuidor", list(distribuidores), format_func=distribuidores.get,
                     key="id_distribuidor")

# --- Paso 4: resumen, confirmar y guardar ---
st.subheader("4. Resumen")
if carrito:
    try:
        # Mismas unidades que se venderian al confirmar, para que el margen sea exacto
        ids = funciones_bd.elegir_prendas(carrito)
        datos = {fila[0]: fila for fila in funciones_bd.prendas_para_venta()}
        total = sum(datos[i][4] for i in ids)
        margen = sum(datos[i][5] for i in ids)
        col1, col2 = st.columns(2)
        col1.metric("Total a cobrar", pesos(total))
        col2.metric("Margen total", pesos(margen))
        st.caption(str(len(ids)) + " prenda(s) en esta venta.")
    except ValueError as error:
        # por ejemplo, si otra venta se llevo unidades mientras se armaba esta
        st.error(str(error) + " Quita ese producto y vuelve a agregarlo.")
else:
    st.caption("Agrega al menos un producto para ver el resumen.")

# Confirmacion para no registrar una venta por accidente
st.checkbox("Revisé el resumen y quiero registrar esta venta", key="confirmo_venta")
st.button("Confirmar venta", type="primary", on_click=confirmar_venta, width="stretch",
          disabled=not st.session_state.confirmo_venta)

if "error_venta" in st.session_state:
    st.error("No se guardó la venta. " + st.session_state.pop("error_venta"))

if "ultimo_pedido" in st.session_state:
    id_pedido, clienta, fecha, cantidad, total, margen = funciones_bd.obtener_pedido(
        st.session_state.ultimo_pedido)
    st.success("Venta registrada: pedido N° " + str(id_pedido) + " de " + clienta + ", " +
               str(cantidad) + " prenda(s), total " + pesos(total) + ", margen " + pesos(margen) +
               ". Queda pendiente en Entregas.")
