# Pantalla "Inventario" (RF-09): resumen por estado, stock por producto y detalle por prenda

import pandas as pd
import streamlit as st

import funciones_bd

NOMBRES_ESTADO = {
    "disponible": "Disponible",
    "en_remate": "En remate",
    "vendida": "Vendida",
    "entregada": "Entregada",
}


def texto_stock(en_stock, en_remate):
    # 10, 0 -> "10 un" / 10, 2 -> "10 un (2 en remate)" / 0, 0 -> "Sin stock"
    if en_stock == 0:
        return "Sin stock"
    if en_remate > 0:
        return str(en_stock) + " un (" + str(en_remate) + " en remate)"
    return str(en_stock) + " un"


st.header("Inventario")

# --- Resumen por estado ---
resumen = dict(funciones_bd.inventario_por_estado())

# Stock para vender = disponible + en remate (regla R2 de ../docs/08-supuestos.md)
st.metric("Stock para vender", resumen["disponible"] + resumen["en_remate"])

# En el celular Streamlit apila las columnas una debajo de otra
col1, col2 = st.columns(2)
col1.metric(NOMBRES_ESTADO["disponible"], resumen["disponible"])
col2.metric(NOMBRES_ESTADO["en_remate"], resumen["en_remate"])
col1.metric(NOMBRES_ESTADO["vendida"], resumen["vendida"])
col2.metric(NOMBRES_ESTADO["entregada"], resumen["entregada"])

# --- Stock por producto (tipo + talla) ---
st.subheader("Stock por producto")
productos = pd.DataFrame(funciones_bd.stock_por_producto(),
                         columns=["Prenda", "Talla", "En stock", "En remate"])

if productos.empty:
    st.info("Todavía no hay prendas registradas.")
else:
    productos["Stock"] = [texto_stock(s, r) for s, r in zip(productos["En stock"], productos["En remate"])]

    tipos = ["Todos"] + sorted(productos["Prenda"].unique().tolist())
    tipo_elegido = st.selectbox("Tipo de prenda", tipos)
    mostrar_sin_stock = st.checkbox("Mostrar productos sin stock", value=True)

    if tipo_elegido != "Todos":
        productos = productos[productos["Prenda"] == tipo_elegido]
    if not mostrar_sin_stock:
        productos = productos[productos["En stock"] > 0]

    if productos.empty:
        st.info("No hay productos para mostrar con este filtro.")
    else:
        st.dataframe(productos[["Prenda", "Talla", "Stock"]], hide_index=True, width="stretch")

    # --- Detalle: cada prenda en stock con su ID (se usara en ventas y remates) ---
    with st.expander("Ver cada prenda (ID, precio y días en stock)"):
        filas = funciones_bd.stock_disponible()
        detalle = pd.DataFrame(filas, columns=["ID", "Tipo", "Talla", "Precio venta",
                                               "Precio remate", "Estado", "Días en stock"])
        detalle["Estado"] = detalle["Estado"].map(NOMBRES_ESTADO)
        if tipo_elegido != "Todos":
            detalle = detalle[detalle["Tipo"] == tipo_elegido]

        if detalle.empty:
            st.info("No hay prendas en stock con este filtro.")
        else:
            st.caption(str(len(detalle)) + " prendas. Días en stock = días desde que llegó el lote.")
            st.dataframe(
                detalle,
                hide_index=True,
                width="stretch",
                column_config={
                    "Precio venta": st.column_config.NumberColumn(format="$%d"),
                    "Precio remate": st.column_config.NumberColumn(format="$%d"),
                },
            )
