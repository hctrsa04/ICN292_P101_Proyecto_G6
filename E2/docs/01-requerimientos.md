# Requerimientos (definidos en la Entrega 1)

> Actores y roles: ver `E1/docs/01-requerimientos.md`. Las rutas de código y pruebas de este documento son relativas a `E2/app/`.

Prioridad MoSCoW: M = debe (Must), S = debería (Should), C = podría (Could).

## Requerimientos funcionales

| ID | Requerimiento | Prioridad | Justificación |
|---|---|---|---|
| RF-01 | El sistema debe permitir registrar un lote de prendas indicando fecha de recepción y costo total del lote. | M | Belén no tiene registro de cuánto pagó por cada lote, lo que impide calcular márgenes. |
| RF-02 | El sistema debe generar automáticamente una ficha individual por prenda al registrar un lote, incluyendo descripción, talla, precio sugerido y estado (disponible). | M | Las prendas se gestionan de memoria; no existe inventario estructurado. |
| RF-03 | El sistema debe registrar una venta asociando la prenda vendida, el precio cobrado, la fecha y el cliente. | M | Las ventas no quedan registradas, lo que impide analizar ingresos o detectar errores. |
| RF-04 | El sistema debe calcular y almacenar automáticamente el margen de ganancia por prenda al momento de registrar la venta. | M | Belén desconoce la rentabilidad real de cada transacción. |
| RF-05 | El sistema debe registrar o actualizar los datos del cliente (nombre, contacto) en cada venta. | M | No existe historial de clientes. |
| RF-06 | El sistema debe generar una ficha de publicación por prenda con la información necesaria para subir a Instagram. | S | El proceso de publicación es manual y repetitivo. |
| RF-07 | El sistema debe detectar prendas que superen un umbral configurable de días sin venta y generar una alerta de remate. | S | Las prendas con bajo movimiento no generan ninguna señal. |
| RF-08 | El sistema debe permitir marcar una prenda como entregada y registrar la fecha de entrega al confirmar el despacho. | M | El cierre del proceso (entrega) no queda registrado. |
| RF-09 | El sistema debe mostrar un resumen de inventario con prendas disponibles, vendidas y entregadas. | S | Belén no tiene visibilidad del estado actual de su stock. |
| RF-10 | El sistema debe permitir configurar el umbral de días sin venta que activa la alerta de remate. | C | El umbral óptimo depende del contexto del negocio y puede variar. |

## Requerimientos no funcionales

| ID | Requerimiento | Prioridad | Justificación |
|---|---|---|---|
| RNF-01 | La interfaz debe ser operable desde un smartphone sin capacitación técnica previa. | M | Belén es la única usuaria y gestiona el negocio desde su teléfono. |
| RNF-02 | El sistema debe estar disponible al menos el 95 % del tiempo en horario de operación (09:00–22:00). | M | Las ventas ocurren a cualquier hora vía Instagram. (En localhost no se puede garantizar: limitación declarada.) |
| RNF-03 | El acceso al sistema debe requerir autenticación con contraseña. | S | Los datos de clientes y márgenes son información sensible. |
| RNF-04 | El tiempo de respuesta de cualquier operación de registro o consulta debe ser inferior a 3 segundos. | S | Una herramienta lenta será abandonada. |
| RNF-05 | El sistema debe poder ser mantenido o extendido por un desarrollador sin conocimiento previo, dado un README adecuado. | C | La sostenibilidad no debe depender de un único desarrollador. |

## Trazabilidad: dónde está implementado cada requisito y cómo se prueba

Estado al cierre de la Entrega 2 (21-nov-2026). Cubierto = cumple el requisito; Parcial = cumple una parte (se indica cuál falta); No cubierto = no se implementó. Las pruebas se ejecutan con `python -m unittest discover -s tests -v`.

| Req. | Estado | Dónde está implementado | Cómo se prueba |
|---|---|---|---|
| RF-01 | Cubierto | `registrar_lote()` en `funciones_bd.py`; pantalla `app/paginas/registrar_lote.py` | `tests/test_registrar_lote.py`; `test_registrar_lote_desde_la_pantalla` |
| RF-02 | Cubierto (con matiz) | `registrar_lote()` crea una ficha por unidad con tipo, talla, costo, precio y estado `disponible`. La "descripción" es el **tipo** (el esquema no tiene campo descripción) | `test_crea_una_prenda_disponible_por_cada_elemento`, `test_cantidad_crea_una_ficha_por_unidad` |
| RF-03 | Parcial | `registrar_venta()` y `registrar_venta_por_producto()`; pantalla `registrar_venta.py`. **Falta:** el precio cobrado es siempre el publicado o el de remate, no un precio editable (P2 en `08-supuestos.md`) | `tests/test_venta_y_entregas.py`; `test_venta_por_producto_con_clienta_nueva_y_doble_clic` |
| RF-04 | Cubierto | `registrar_venta()` calcula y guarda `DetallePedido.margen` = precio_final − costo de la prenda | `test_registrar_venta_descuenta_stock_y_calcula_margen`, `test_prenda_en_remate_se_cobra_a_precio_de_remate` |
| RF-05 | Parcial | Registrar: clienta nueva en la misma transacción de la venta, o elegir una existente con `buscar_clientas()` (R3). **Falta:** actualizar los datos de una clienta existente | `test_clienta_nueva_se_crea_y_queda_en_el_pedido`, `test_si_la_venta_falla_no_queda_la_clienta_nueva_ni_el_pedido` |
| RF-06 | Parcial | `generar_ficha_publicacion()`; pantalla `publicar.py` (texto para copiar y fila en `Publicacion`). **Falta:** la foto (`Publicacion.foto` queda vacía) | `tests/test_publicacion.py`; `test_publicar_producto_en_remate` |
| RF-07 | Cubierto | `generar_alertas()` en `alerta_remate.py` (terminal, `ejecutar_alerta.bat` y botón "Revisar ahora"); se atiende con `atender_alerta()` en la pantalla `alertas.py` | `tests/test_alertas.py`; `test_revisar_ahora_crea_7_y_luego_0` |
| RF-08 | Cubierto | `marcar_entregado()`; pantalla `entregas.py` con confirmación | `test_venta_nueva_aparece_y_al_entregar_sale`, `test_entregas_marcar_entregado_con_confirmacion` |
| RF-09 | Cubierto | `inventario_por_estado()`, `stock_por_producto()` y `stock_disponible()`; pantalla `inventario.py` | `PruebasInventario`; `test_inventario_muestra_resumen_por_estado` |
| RF-10 | Cubierto | `obtener_umbral()` y `actualizar_umbral()`; formulario de umbral en `alertas.py` | `test_umbral_invalido_no_cambia_nada`, `test_umbral_40_y_revisar_crea_3` |
| RNF-01 | Cubierto | Una columna (`layout="centered"`), menú arriba, botones a todo el ancho, formularios cortos, confirmaciones | **Prueba manual** en celular (sección 4 del README). No hay prueba automática |
| RNF-02 | **No cubierto** | Corre en `localhost`: la disponibilidad depende de que el computador esté encendido. Limitación declarada en el README | No aplica |
| RNF-03 | Cubierto | Acceso con clave de `st.secrets["clave_acceso"]` en `app/main.py`; "Cerrar sesión". La clave no se cambia desde la app (L3) | `PruebasAcceso` en `tests/test_app_esqueleto.py` |
| RNF-04 | Cubierto | Consultas cortas a SQLite, sin cálculos pesados | `python medir_tiempos.py`: peor tiempo 1,39 s (pantalla Alertas con 1.343 alertas) en una base de 3.026 prendas. Mide el servidor, no el dibujo en el navegador |
| RNF-05 | Cubierto | `README.md`, código comentado en español, decisiones en `docs/` | Prueba de reproducibilidad siguiendo el README en una carpeta limpia |

Tablero KPI (K1 a K5): `kpis.py` y `app/paginas/tablero.py`; se prueba con `tests/test_kpis.py` y `test_tablero`. Ver `05-kpi-dashboard.md`.
