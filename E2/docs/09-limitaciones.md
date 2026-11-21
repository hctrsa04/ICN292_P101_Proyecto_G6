# Limitaciones encontradas en el desarrollo

> Las rutas de código de este documento son relativas a `E2/app/`.

En este documento se registran las limitaciones encontradas durante el desarrollo de la app del SIG Alta Facha: funcionalidades que se pidieron o se evaluaron y que no se implementaron, o que se implementaron solo en parte. Para cada una se indica el motivo, cómo funciona hoy la app y qué se podría hacer más adelante.

| N° | Limitación | Pantalla | Estado |
|----|------------|----------|--------|
| L1 | No se pueden eliminar productos sin stock del inventario | Inventario | Abierta |
| L2 | El precio de remate no puede quedar bajo el costo (margen ≥ 0 %) | Alertas | Abierta |
| L3 | La clave de acceso no se puede cambiar ni restablecer desde la app | Acceso | Abierta |
| L4 | Las metas de los KPI no se pueden definir ni editar desde la app | Tablero | Abierta |

---

## L1. No se pueden eliminar productos sin stock del inventario

**Qué se pidió.** Alta Facha tiene alta rotación de productos por temporada. Se pidió que Belén pudiera eliminar del inventario un producto (tipo + talla, por ejemplo "vestido rojo, talla S") cuando ya no le queden unidades.

**Por qué no se puede borrar.** Un producto sin stock está formado por prendas en estado `vendida` o `entregada`. Cada una está ligada a su venta en `DetallePedido`, que guarda el precio cobrado y el margen. Si se borraran esas prendas (`DELETE`):

- la base lo impide, porque `DetallePedido.id_prenda` es una llave foránea hacia `Prenda`;
- y si se forzara, se perdería el historial de ventas, y con él los ingresos, los márgenes y los KPI del tablero.

**Alternativa evaluada y descartada.** La alternativa era "archivar" en vez de borrar: agregar una columna `Prenda.oculta` (0/1) para quitar el producto solo de la lista del inventario, sin tocar las ventas. El equipo no la aprobó porque agrega complejidad al esquema (`sql/schema.sql`).

**Cómo funciona hoy.** La pantalla Inventario agrupa el stock por producto y muestra "Sin stock" cuando no quedan unidades. La casilla **"Mostrar productos sin stock"** permite ocultar **todos** los productos sin stock a la vez, pero no uno por uno. Esa preferencia no se guarda, así que la casilla vuelve a quedar marcada al abrir la app de nuevo.

**Impacto.** Con cada temporada se acumulan productos sin stock en la lista. Se mitiga con la casilla y con el filtro por tipo de prenda.

**Posibles soluciones futuras** (todas requieren aprobar un cambio de esquema):

1. Columna `Prenda.oculta`. Es la alternativa descrita arriba: las unidades nuevas de un producto quitado vuelven a aparecer solas.
2. Una tabla aparte `ProductoOculto (tipo, talla)`. Requiere borrar la fila cuando llega stock nuevo de ese producto.
3. Mostrar por defecto solo los productos vendidos en los últimos N días. No cambia el esquema, pero hay que acordar N con Belén.

---

## L2. El precio de remate no puede quedar bajo el costo (margen ≥ 0 %)

**Qué se definió.** Cuando una prenda supera el umbral de días sin venta, Belén atiende la alerta e ingresa un margen de remate sobre el costo de la prenda. La app calcula el precio de remate como `costo × (1 + margen)`. Por ejemplo, con un costo de $3.000 y un margen de 100 % el precio de remate queda en $6.000. La app **solo acepta márgenes mayores o iguales a 0 %**, así que el precio de remate nunca queda bajo lo que costó la prenda.

**Por qué.** Hoy Belén remata para que la prenda rote, pero sin perder plata: el remate baja el precio de venta, no por debajo del costo. La validación refleja ese modo de trabajo y evita errores de tipeo, como un margen negativo por accidente.

**Dónde está.** En `atender_alerta()` (`funciones_bd.py`), que rechaza un margen negativo, y en la pantalla Alertas, donde el campo "Margen sobre el costo (%)" no acepta valores bajo 0 (`min_value=0`). Hay pruebas en `tests/test_alertas.py`.

**Impacto si cambia el negocio.** Si en el futuro Belén necesita liquidar con pérdida, por ejemplo fin de temporada al 50 % del costo, la app no lo permitiría.

**Ajuste necesario en ese caso** (no requiere cambiar el esquema; `AlertaRemate.margen_remate` ya acepta decimales negativos):

1. En `atender_alerta()`, cambiar la condición `margen < 0` por `margen <= -1`, para que el precio siga siendo mayor que $0.
2. En la pantalla Alertas, cambiar `min_value=0` por un mínimo negativo, por ejemplo `-99`, y mostrar un aviso cuando el precio de remate quede bajo el costo.
3. Actualizar el test `test_margen_invalido_no_cambia_nada`.
4. Considerar que el margen de la venta (`DetallePedido.margen`) podría quedar negativo, y revisar cómo lo muestran los KPI del tablero.

---

## L3. La clave de acceso no se puede cambiar ni restablecer desde la app

**Qué se pidió.** Que Belén pudiera cambiar o restablecer la clave de acceso con un botón dentro de la app, sin editar archivos.

**Cómo funciona hoy.** La clave se define en el archivo `.streamlit/secrets.toml`, en la línea `clave_acceso = "..."`. Ese archivo no se sube a GitHub (`.gitignore`). Para cambiar la clave:

1. Abrir `.streamlit/secrets.toml` con un editor de texto. Si no existe, copiarlo desde `.streamlit/secrets.toml.example`.
2. Reemplazar el texto entre comillas por la clave nueva, manteniendo las comillas.
3. Guardar y reiniciar la app (`Ctrl+C` y `streamlit run app/main.py`).

Si Belén olvida la clave, quien le da soporte la lee o la cambia en ese mismo archivo.

**Por qué no se implementó.**

- **Cambiar la clave desde la app** obliga a guardarla en un lugar donde la app pueda escribir. La opción evaluada fue agregar una columna `Configuracion.clave_hash` con un hash de la clave (`hashlib.pbkdf2_hmac`, de la biblioteca estándar). Eso implica un cambio de esquema y modificar la regla del proyecto de que la clave sale de `st.secrets`. Por el plazo de entrega se decidió mantener el funcionamiento actual.
- **Restablecer una clave olvidada** no debe hacerse con un botón dentro de la app: cualquiera que abra la página podría restablecerla y la clave dejaría de proteger los datos de clientas y márgenes (RNF-03). Ese paso tiene que hacerse fuera de la app.

**Impacto.** Belén depende de alguien con acceso al computador donde corre la app para cambiar la clave. Como la app es local y la usa una sola persona, el impacto es bajo.

**Posible solución futura** (requiere aprobar el cambio de esquema):

1. Agregar `clave_hash TEXT` a `Configuracion`. La clave de `secrets.toml` queda como clave inicial.
2. Agregar una sección "Cambiar clave" en la app, con clave actual, clave nueva y repetir clave nueva. Guarda solo el hash, nunca la clave en texto.
3. Agregar un script `restablecer_clave.py`, que se ejecuta en el computador, para borrar el hash y volver a la clave inicial si Belén la olvida.

---

## L4. Las metas de los KPI no se pueden definir ni editar desde la app

**Qué se pidió.** Que Belén pudiera escribir y editar la meta de cada KPI desde el tablero, en un cuadro de texto.

**Cómo funciona hoy.** Las metas están fijas en el código y se muestran en el desplegable "ℹ️ Cómo se calculan estos indicadores", al final del tablero:

- **K4:** "≥ 2,0 veces la inversión (duplicar lo invertido), según Belén (informe E2)". Es la única meta definida hoy. El valor 2,0 está en `kpis.py` (`META_K4`) y se usa para marcar cada lote como "✅ Alcanzó" o "⏳ Aún no".
- **K1, K2, K3 y K5:** "Por definir con Belén". Las metas no se inventan (`docs/05-kpi-dashboard.md`).

Para cambiar una meta, el equipo edita `META_K4` en `kpis.py` o el texto de `FICHAS_KPI` en `app/paginas/tablero.py`, y actualiza `docs/05-kpi-dashboard.md`.

**Por qué no se implementó.** Para que las metas editadas no se pierdan al recargar la página, hay que guardarlas en la base. Eso requiere una tabla nueva (`MetaKpi`), es decir, un cambio de esquema y de los datos de prueba. Por el plazo de entrega se priorizó un MVP y se mantuvieron las metas fijas.

**Impacto.** Cuando Belén defina las metas de K1, K2, K3 y K5, o quiera cambiar la de K4, depende del equipo para actualizarlas. Mientras tanto, el tablero muestra "Por definir con Belén", que es el estado real de esas metas.

**Posible solución futura** (requiere aprobar el cambio de esquema):

1. Crear la tabla `MetaKpi (codigo TEXT PRIMARY KEY, meta TEXT NOT NULL, valor REAL)`. `valor` se usa solo en K4 para comparar con cada lote. La tabla sigue en 3FN.
2. Cargar en `datos_prueba.sql` las metas de hoy: K4 = 2,0 y las demás "Por definir con Belén".
3. Agregar `actualizar_meta(codigo, meta, valor)` en `funciones_bd.py` y un formulario "Editar metas" en el tablero.
4. Hacer que el "✅ Alcanzó / ⏳ Aún no" de K4 use el valor guardado en vez de `META_K4`.
