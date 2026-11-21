# Punto de entrada de la app Streamlit del SIG Alta Facha
# Ejecutar desde la carpeta raiz del proyecto:  streamlit run app/main.py

import hmac
import os
import sys

import streamlit as st

# Streamlit solo agrega la carpeta app/ a la ruta de Python. Agregamos la carpeta
# raiz para poder importar funciones_bd.py (y mas adelante kpis.py).
carpeta_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if carpeta_raiz not in sys.path:
    sys.path.insert(0, carpeta_raiz)

import funciones_bd  # noqa: E402

# layout "centered" = una sola columna angosta, comoda en el celular (RNF-01)
st.set_page_config(page_title="Alta Facha — SIG", layout="centered")

st.title("Alta Facha — SIG")

# --- Acceso con contraseña (RNF-03) ---
# La clave vive en .streamlit/secrets.toml, que no se sube a GitHub (.gitignore).
try:
    clave_correcta = str(st.secrets["clave_acceso"])
except (FileNotFoundError, KeyError):
    st.error("Falta configurar la clave de acceso. En la carpeta del proyecto, copia el archivo "
             "`.streamlit/secrets.toml.example` como `.streamlit/secrets.toml`, cambia la clave "
             "que aparece ahí y vuelve a iniciar la app.")
    st.stop()


def iniciar_sesion():
    ingresada = st.session_state.get("clave_ingresada", "")
    # compare_digest compara en tiempo constante: no da pistas sobre la clave
    if hmac.compare_digest(ingresada.encode(), clave_correcta.encode()):
        st.session_state.autenticada = True
    else:
        st.session_state.error_acceso = True
    st.session_state.clave_ingresada = ""  # no dejar la clave escrita en el campo


def cerrar_sesion():
    # Borra todo lo de la sesion (incluye carritos a medio armar) y vuelve a pedir la clave
    st.session_state.clear()


# La sesion dura mientras la pestaña este abierta. Si se recarga la pagina, Streamlit
# crea una sesion nueva y vuelve a pedir la clave.
if not st.session_state.get("autenticada"):
    with st.form("form_acceso"):
        st.text_input("Clave de acceso", type="password", key="clave_ingresada")
        st.form_submit_button("Entrar", on_click=iniciar_sesion, type="primary", width="stretch")
    if st.session_state.pop("error_acceso", False):
        st.error("Clave incorrecta.")
    st.stop()  # sin la clave correcta no se carga nada mas de la app

# Si la base no existe, sqlite3.connect crearia un archivo vacio sin tablas y
# las pantallas fallarian con errores confusos. Mejor avisar y detenerse.
if not os.path.exists(funciones_bd.ruta_bd):
    st.error("No se encontró la base de datos. Primero ejecuta en la terminal: "
             "`python crear_bd.py`")
    st.stop()

# Menu arriba (position="top") porque en el celular la barra lateral queda escondida
paginas = [
    st.Page("paginas/inventario.py", title="Inventario", default=True),
    st.Page("paginas/registrar_lote.py", title="Registrar lote"),
    st.Page("paginas/registrar_venta.py", title="Registrar venta"),
    st.Page("paginas/entregas.py", title="Entregas"),
    st.Page("paginas/alertas.py", title="Alertas"),
    st.Page("paginas/publicar.py", title="Publicar"),
    st.Page("paginas/tablero.py", title="Tablero"),
]
pagina_actual = st.navigation(paginas, position="top")
pagina_actual.run()

# Al final de cada pantalla (en el celular la barra lateral queda escondida)
st.divider()
st.button("Cerrar sesión", on_click=cerrar_sesion, width="stretch")
