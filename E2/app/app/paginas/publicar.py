# Pantalla "Publicar" (RF-06): ficha de publicacion lista para copiar a Instagram

import sqlite3

import streamlit as st

import funciones_bd
from formato import pesos


def nombre_producto(tipo, talla, estado, precio):
    texto = tipo + " " + talla + " · " + pesos(precio)
    if estado == "en_remate":
        texto += " (remate)"
    return texto


def generar_ficha():
    tipo, talla, estado, precio = st.session_state.producto_publicar
    producto = {"tipo": tipo, "talla": talla, "estado": estado, "precio": precio}
    try:
        texto, unidades = funciones_bd.generar_ficha_publicacion(producto)
    except (ValueError, sqlite3.Error) as error:
        st.session_state.error_ficha = "No se generó la ficha. " + str(error)
        return
    # Se guarda el producto junto al texto para mostrar la ficha solo mientras siga elegido
    st.session_state.ficha = (st.session_state.producto_publicar, texto, unidades)


st.header("Publicar")
st.caption("Elige un producto, genera su ficha y cópiala en Instagram.")

productos = {}
for tipo, talla, estado, precio, unidades in funciones_bd.productos_para_venta():
    productos[(tipo, talla, estado, precio)] = unidades

if not productos:
    st.info("No hay prendas disponibles para publicar.")
else:
    st.selectbox(
        "Producto (escribe para buscar)",
        list(productos),
        format_func=lambda p: nombre_producto(*p) + " · " + str(productos[p]) + " disp.",
        key="producto_publicar",
    )
    elegido = st.session_state.producto_publicar
    tipo, talla, estado, precio = elegido
    fecha = funciones_bd.ultima_publicacion({"tipo": tipo, "talla": talla, "estado": estado, "precio": precio})
    st.caption("Última publicación: " + fecha if fecha else "Todavía no se ha publicado.")

    st.button("Generar ficha", type="primary", on_click=generar_ficha, width="stretch")

    if "error_ficha" in st.session_state:
        st.error(st.session_state.pop("error_ficha"))

    ficha = st.session_state.get("ficha")
    if ficha and ficha[0] == elegido:
        _, texto, unidades = ficha
        st.success("Ficha generada y guardada (" + str(unidades) + " unidad(es)).")
        # Cuadro de texto y no st.code: el boton de copiar de st.code solo funciona en
        # paginas "seguras" (https o localhost); desde el celular (http://192.168...) el
        # navegador lo bloquea. Mantener presionado y copiar funciona en cualquier celular.
        # Si Belen edita el texto aqui, no cambia lo guardado en la base.
        st.caption("Para copiar: mantén presionado el texto → Seleccionar todo → Copiar.")
        st.text_area("Ficha para Instagram", value=texto, height=150)
