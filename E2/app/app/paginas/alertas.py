# Pantalla "Alertas" (RF-07, RF-10): umbral, revisar ahora y atender alertas de remate

import sqlite3

import streamlit as st

import alerta_remate
import funciones_bd
from formato import pesos


def guardar_umbral():
    # Callback del formulario: se guarda antes de redibujar, asi el texto de arriba ya
    # muestra el umbral nuevo.
    try:
        funciones_bd.actualizar_umbral(st.session_state.nuevo_umbral)
    except ValueError as error:
        st.session_state.error_alertas = str(error)
        return
    st.session_state.aviso_alertas = "Umbral guardado: " + str(st.session_state.nuevo_umbral) + " días."


def revisar_ahora():
    # Misma revision que hace alerta_remate.py desde la terminal, sobre la base de la app
    try:
        nuevas = alerta_remate.generar_alertas(funciones_bd.ruta_bd)
    except sqlite3.Error:
        st.session_state.error_alertas = "No se pudo revisar el stock. Intenta de nuevo."
        return
    if nuevas:
        st.session_state.aviso_alertas = "Se crearon " + str(len(nuevas)) + " alertas nuevas."
    else:
        st.session_state.aviso_alertas = "No hay alertas nuevas."


def poner_en_remate(id_alerta, id_prenda, nombre):
    porcentaje = st.session_state.get("margen_" + str(id_alerta))
    if porcentaje is None:
        st.session_state.error_alertas = "Ingresa el margen de remate."
        return
    try:
        # Belen escribe el margen en % (100) y en la base se guarda como 1.0, igual que hoy
        precio = funciones_bd.atender_alerta(id_alerta, porcentaje / 100)
    except (ValueError, sqlite3.Error) as error:
        st.session_state.error_alertas = "No se puso en remate. " + str(error)
        return
    st.session_state.aviso_alertas = ("Prenda N° " + str(id_prenda) + " (" + nombre + ") en remate a " +
                                      pesos(precio) + ".")


st.header("Alertas de remate")

if "aviso_alertas" in st.session_state:
    st.success(st.session_state.pop("aviso_alertas"))
if "error_alertas" in st.session_state:
    st.error(st.session_state.pop("error_alertas"))

# --- Umbral ---
st.subheader("Umbral de días sin venta")
umbral = funciones_bd.obtener_umbral()
st.write("Se crea una alerta cuando una prenda disponible supera los **" + str(umbral) +
         " días** desde que llegó su lote.")
with st.form("form_umbral"):
    st.number_input("Nuevo umbral (días)", min_value=1, step=1, value=umbral, key="nuevo_umbral")
    st.form_submit_button("Guardar umbral", on_click=guardar_umbral, width="stretch")

# --- Revisar ahora ---
st.subheader("Revisar stock")
st.caption("Busca prendas que superen el umbral y crea sus alertas. Revisar dos veces no duplica alertas.")
st.button("Revisar ahora", type="primary", on_click=revisar_ahora, width="stretch")

# --- Alertas pendientes ---
st.subheader("Alertas pendientes")
pendientes = funciones_bd.alertas_pendientes()

if not pendientes:
    st.info("No hay alertas pendientes.")
else:
    st.caption(str(len(pendientes)) + " alerta(s), las prendas con más días primero.")
    for id_alerta, id_prenda, tipo, talla, costo, precio_venta, dias, fecha in pendientes:
        nombre = tipo + " " + talla
        with st.container(border=True):
            st.markdown("**Prenda N° " + str(id_prenda) + "** · " + nombre)
            st.text("Costo " + pesos(costo) + " · Precio de venta " + pesos(precio_venta))
            st.text(str(dias) + " días sin venta (alerta del " + fecha + ")")

            porcentaje = st.number_input("Margen sobre el costo (%)", min_value=0, step=10, value=None,
                                         placeholder="Ej: 100", key="margen_" + str(id_alerta))
            if porcentaje is not None:
                precio_remate = funciones_bd.calcular_precio_remate(costo, porcentaje / 100)
                st.write("Precio de remate: **" + pesos(precio_remate) + "**")
                if precio_remate >= precio_venta:
                    st.warning("Ojo: el precio de remate no es menor que el precio de venta (" +
                               pesos(precio_venta) + ").")
            st.button("Poner en remate", key="remate_" + str(id_alerta), on_click=poner_en_remate,
                      args=(id_alerta, id_prenda, nombre), width="stretch",
                      disabled=porcentaje is None)
