# Pantalla "Entregas" (RF-08): pedidos pendientes y boton "Marcar entregado"

import sqlite3

import streamlit as st

import funciones_bd
from formato import pesos


def entregar(id_pedido):
    # Callback del boton: marca el pedido antes de redibujar, asi desaparece de la lista
    try:
        funciones_bd.marcar_entregado(id_pedido)
    except sqlite3.Error:
        st.session_state.error_entrega = "No se pudo marcar el pedido N° " + str(id_pedido) + ". Intenta de nuevo."
        return
    st.session_state.pedido_entregado = id_pedido


st.header("Entregas")

if "pedido_entregado" in st.session_state:
    st.success("Pedido N° " + str(st.session_state.pop("pedido_entregado")) + " marcado como entregado.")
if "error_entrega" in st.session_state:
    st.error(st.session_state.pop("error_entrega"))

pendientes = funciones_bd.pedidos_pendientes_entrega()

if not pendientes:
    st.info("No hay entregas pendientes 🎉")
else:
    st.caption(str(len(pendientes)) + " pedido(s) por entregar, los más antiguos primero.")
    for id_pedido, fecha, clienta, contacto, tipo_entrega, distribuidor, prendas, total, dias in pendientes:
        with st.container(border=True):
            st.markdown("**Pedido N° " + str(id_pedido) + "** · " + clienta)
            if contacto:
                st.text("Contacto: " + contacto)
            st.text("Prendas: " + prendas)
            st.text("Total: " + pesos(total))
            entrega = "Propia" if tipo_entrega == "propia" else "Distribuidor: " + distribuidor
            st.text(entrega)
            st.text("Vendido el " + fecha + " (hace " + str(dias) + " días)")
            # Confirmacion para no marcar un pedido por accidente (no se puede deshacer desde la app)
            confirmado = st.checkbox("Confirmo que se entregó", key="confirmo_" + str(id_pedido))
            st.button("Marcar entregado", key="entregar_" + str(id_pedido),
                      on_click=entregar, args=(id_pedido,), width="stretch",
                      disabled=not confirmado)
