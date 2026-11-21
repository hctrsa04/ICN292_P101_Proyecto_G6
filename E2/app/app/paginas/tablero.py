# Pantalla "Tablero" (KPI K1 a K5). Todos los numeros salen de kpis.py (consultas a la base).

import pandas as pd
import streamlit as st

import kpis
from formato import pesos

AZUL = "#2a78d6"     # una sola serie
NARANJA = "#eb6834"  # segunda serie (paleta validada para daltonismo)
POR_DEFINIR = "Por definir con Belén"
NOMBRES_ESTADO = {"disponible": "Disponible", "en_remate": "En remate",
                  "vendida": "Vendida", "entregada": "Entregada"}

# Formula, fuente y meta de cada KPI (lo pide el enunciado). Se muestran al final, en un
# desplegable cerrado, para no recargar el tablero. Las metas no se editan desde la app
# (limitacion L4 en ../docs/09-limitaciones.md).
FICHAS_KPI = [
    ("K1 · Inventario por estado", "Conteo de prendas por estado",
     "Prenda.estado", POR_DEFINIR),
    ("K2 · Ventas y margen mensual", "Suma de precio_final y de margen por mes de fecha_venta",
     "DetallePedido (precio_final, margen), Pedido.fecha_venta", POR_DEFINIR),
    ("K3 · Margen bruto", "Suma de margen / suma de precio_final × 100. Margen medio por prenda = "
     "suma de margen / prendas vendidas. No descuenta despacho",
     "DetallePedido (precio_final, margen)", POR_DEFINIR),
    ("K4 · Recuperación de la inversión", "Veces la inversión = ventas / costo_total del lote. "
     "Resultado neto = ventas − costo_total; % vendido",
     "Lote (costo_total, cantidad_prendas), Prenda, DetallePedido.precio_final",
     "≥ 2,0 veces la inversión (duplicar lo invertido), según Belén (informe E2)"),
    ("K5 · Stock sobre el umbral", "Prendas disponibles con días > umbral / prendas disponibles × 100. "
     "Días desde que llegó el lote",
     "Prenda.estado, Lote.fecha_recepcion, Configuracion.umbral_dias", POR_DEFINIR),
]


def vacio(valor):
    # SQLite devuelve NULL (NaN en pandas) cuando no hay datos, por ejemplo sin ventas
    return valor is None or pd.isna(valor)


def decimal(valor, decimales=1):
    # 79.2 -> "79,2" (coma decimal chilena)
    return f"{valor:.{decimales}f}".replace(".", ",")


st.header("Tablero")
st.warning("Datos de prueba ficticios, no son resultados reales de Alta Facha.")

# --- K1 ---
st.subheader("K1 · Inventario por estado")
k1 = kpis.k1_inventario_por_estado()
k1["Estado"] = k1["estado"].map(NOMBRES_ESTADO)
col1, col2 = st.columns(2)
for i, (estado, prendas) in enumerate(zip(k1["Estado"], k1["prendas"])):
    (col1 if i % 2 == 0 else col2).metric(estado, int(prendas))
st.bar_chart(k1, x="Estado", y="prendas", x_label="", y_label="Prendas", color=AZUL,
             sort=False, height=250)

# --- K2 ---
st.subheader("K2 · Ventas y margen bruto mensual")
k2 = kpis.k2_ventas_margen_mensual()
if k2.empty:
    st.info("Sin ventas registradas.")
else:
    col1, col2 = st.columns(2)
    col1.metric("Ventas (total)", pesos(int(k2["ventas"].sum())))
    col2.metric("Margen (total)", pesos(int(k2["margen"].sum())))
    st.caption(str(int(k2["prendas_vendidas"].sum())) + " prendas vendidas.")
    grafico = k2.rename(columns={"mes": "Mes", "ventas": "Ventas", "margen": "Margen"})
    # Barras agrupadas (no apiladas): el margen es parte de las ventas, apilarlas confundiria
    st.bar_chart(grafico, x="Mes", y=["Ventas", "Margen"], x_label="", y_label="Pesos ($)",
                 color=[AZUL, NARANJA], stack=False, height=280)

# --- K3 ---
st.subheader("K3 · Margen bruto")
k3 = kpis.k3_margen_bruto().iloc[0]
if vacio(k3["margen_pct"]):
    st.info("Sin ventas registradas.")
else:
    col1, col2 = st.columns(2)
    col1.metric("Margen bruto", decimal(k3["margen_pct"]) + " %")
    col2.metric("Margen medio por prenda", pesos(int(k3["margen_medio_prenda"])))

# --- K4 ---
st.subheader("K4 · Recuperación de la inversión por lote")
k4 = kpis.k4_recuperacion_por_lote()
if k4.empty:
    st.info("Sin lotes registrados.")
else:
    k4["Lote"] = "Lote " + k4["id_lote"].astype(str)
    # Se compara el mismo valor redondeado que se muestra, asi la tabla no contradice la cifra
    k4["Meta"] = ["✅ Alcanzó" if v >= kpis.META_K4 else "⏳ Aún no" for v in k4["veces_inversion"]]
    alcanzados = (k4["veces_inversion"] >= kpis.META_K4).sum()
    st.metric("Lotes que alcanzan la meta", str(alcanzados) + " de " + str(len(k4)))
    st.bar_chart(k4, x="Lote", y="veces_inversion", x_label="", y_label="Veces la inversión",
                 color=AZUL, sort=False, height=250)
    tabla = pd.DataFrame({
        "Lote": k4["Lote"],
        "Veces": [decimal(v, 2) for v in k4["veces_inversion"]],
        "Meta": k4["Meta"],
        "Resultado neto": [pesos(int(v)) if v >= 0 else "-" + pesos(int(-v)) for v in k4["resultado_neto"]],
        "% vendido": [decimal(v) + " %" for v in k4["pct_vendido"]],
        "Ventas": [pesos(int(v)) for v in k4["ventas"]],
        "Costo lote": [pesos(int(v)) for v in k4["costo_total"]],
    })
    st.dataframe(tabla, hide_index=True, width="stretch")

# --- K5 ---
st.subheader("K5 · Stock sobre el umbral de días sin venta")
k5 = kpis.k5_stock_sobre_umbral().iloc[0]
if vacio(k5["pct_sobre_umbral"]):
    st.info("No hay prendas disponibles.")
else:
    st.metric("Sobre el umbral de " + str(int(k5["umbral_dias"])) + " días",
              decimal(k5["pct_sobre_umbral"]) + " %",
              help="Se cambia en la pantalla Alertas.")
    st.caption(str(int(k5["sobre_umbral"])) + " de " + str(int(k5["disponibles"])) +
               " prendas disponibles.")

# --- Formula, fuente y meta (cerrado por defecto) ---
st.divider()
with st.expander("ℹ️ Cómo se calculan estos indicadores"):
    fichas = pd.DataFrame(FICHAS_KPI, columns=["KPI", "Fórmula", "Fuente", "Meta"])
    fichas["Responsable"] = "Belén"  # todos los KPI los usa y decide Belén (../docs/05-kpi-dashboard.md)
    st.dataframe(fichas, hide_index=True, width="stretch")
