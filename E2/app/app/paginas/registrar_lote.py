# Pantalla "Registrar lote" (RF-01, RF-02)
# Paso 1: datos del lote. Paso 2: agregar prendas una por una. Paso 3: guardar todo junto.

import datetime
import sqlite3

import pandas as pd
import streamlit as st

import funciones_bd
from formato import pesos  # formato de peso chileno, compartido con otras pantallas

PROVEEDOR_NUEVO = "➕ Proveedor nuevo"


# Las prendas agregadas se guardan en la sesion hasta apretar "Guardar lote"
if "prendas_lote" not in st.session_state:
    st.session_state.prendas_lote = []


def quitar_ultima_prenda():
    st.session_state.prendas_lote.pop()


def guardar_lote():
    # Se ejecuta como callback del boton: asi, si sale bien, se pueden limpiar
    # los campos antes de que la pantalla se vuelva a dibujar.
    estado = st.session_state
    if estado.proveedor == PROVEEDOR_NUEVO:
        proveedor = estado.get("nombre_proveedor_nuevo", "")
    else:
        proveedor = estado.proveedor
    try:
        id_lote = funciones_bd.registrar_lote(proveedor, estado.fecha_recepcion.isoformat(),
                                              estado.costo_total, estado.prendas_lote)
    except ValueError as error:
        estado.error_lote = str(error)
        return
    except sqlite3.Error:
        estado.error_lote = "No se pudo guardar el lote y no se guardó nada. Intenta de nuevo."
        return
    estado.lote_guardado = id_lote
    estado.prendas_lote = []
    estado.costo_total = None
    estado.nombre_proveedor_nuevo = ""


st.header("Registrar lote")

# --- Paso 1: datos del lote ---
# Fuera de un st.form para que el campo "proveedor nuevo" aparezca apenas se elige
st.subheader("1. Datos del lote")
proveedores = funciones_bd.listar_proveedores()
nombres_proveedor = dict(proveedores)
st.selectbox(
    "Proveedor",
    list(nombres_proveedor) + [PROVEEDOR_NUEVO],
    format_func=lambda opcion: nombres_proveedor.get(opcion, opcion),
    key="proveedor",
)
if st.session_state.proveedor == PROVEEDOR_NUEVO:
    st.text_input("Nombre del proveedor nuevo", key="nombre_proveedor_nuevo")

# date.today() usa la hora del computador donde corre la app (Chile), igual que
# 'localtime' en SQLite. No usamos zoneinfo porque en Windows necesita otra libreria.
st.date_input("Fecha de recepción", value=datetime.date.today(),
              format="DD/MM/YYYY", key="fecha_recepcion")
st.number_input("Costo total del lote ($)", min_value=0, step=1000, value=None,
                key="costo_total")

# --- Paso 2: prendas ---
st.subheader("2. Prendas")
with st.form("form_prenda", clear_on_submit=True):
    st.text_input("Tipo de prenda", placeholder="Ej: vestido rojo", key="prenda_tipo")
    st.text_input("Talla", placeholder="Ej: M", key="prenda_talla")
    st.number_input("Cantidad de unidades", min_value=1, step=1, value=1,
                    key="prenda_cantidad")
    st.number_input("Costo por unidad ($)", min_value=0, step=500, value=None,
                    key="prenda_costo")
    st.number_input("Precio de venta por unidad ($)", min_value=0, step=500, value=None,
                    key="prenda_precio")
    agregar = st.form_submit_button("Agregar prenda", width="stretch")

if agregar:
    prenda = {
        "tipo": st.session_state.prenda_tipo,
        "talla": st.session_state.prenda_talla,
        "costo": st.session_state.prenda_costo,
        "precio_venta": st.session_state.prenda_precio,
        "cantidad": st.session_state.prenda_cantidad,
    }
    error = funciones_bd.validar_prenda(prenda)
    if error:
        st.error("No se agregó la prenda. " + error)
    else:
        # Se normaliza al agregar para que la lista muestre lo que se va a guardar
        prenda = funciones_bd.normalizar_prenda(prenda)
        st.session_state.prendas_lote.append(prenda)
        st.success("Agregado: " + str(prenda["cantidad"]) + " × " + prenda["tipo"] +
                   " talla " + prenda["talla"])

prendas = st.session_state.prendas_lote
if prendas:
    total_unidades = sum(p["cantidad"] for p in prendas)
    st.write("Prendas agregadas: **" + str(total_unidades) + " unidades**")
    lista = pd.DataFrame(prendas)[["cantidad", "tipo", "talla", "costo", "precio_venta"]]
    lista.columns = ["Cantidad", "Tipo", "Talla", "Costo c/u", "Precio c/u"]
    lista.index = range(1, len(lista) + 1)
    st.dataframe(lista, width="stretch")
    st.button("Quitar última prenda", on_click=quitar_ultima_prenda, width="stretch")

    # Aviso informativo, no impide guardar.
    # TODO(equipo): P1 en ../docs/08-supuestos.md. Si se decide otra regla, cambiar aqui.
    suma_costos = sum(p["costo"] * p["cantidad"] for p in prendas)
    costo_total = st.session_state.costo_total
    if costo_total and suma_costos != costo_total:
        st.info("La suma de los costos de las prendas (" + pesos(suma_costos) +
                ") es distinta del costo total del lote (" + pesos(costo_total) + ").")
else:
    st.caption("Todavía no hay prendas en este lote.")

# --- Paso 3: guardar ---
st.subheader("3. Guardar")
st.button("Guardar lote", type="primary", on_click=guardar_lote, width="stretch")

if "error_lote" in st.session_state:
    st.error("No se guardó el lote. " + st.session_state.pop("error_lote"))

if "lote_guardado" in st.session_state:
    id_lote = st.session_state.pop("lote_guardado")
    _, proveedor, fecha, costo, cantidad = funciones_bd.obtener_lote(id_lote)
    st.success("Lote N° " + str(id_lote) + " guardado: " + str(cantidad) + " prendas de " +
               proveedor + ", recibido el " + fecha + ", costo total " + pesos(costo) + ".")
    creadas = pd.DataFrame(funciones_bd.prendas_de_lote(id_lote),
                           columns=["ID", "Tipo", "Talla", "Costo", "Precio venta", "Estado"])
    st.dataframe(creadas, hide_index=True, width="stretch")
