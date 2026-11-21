# CHANGELOG

Registro de los cambios relevantes entre la Entrega 1 (E1) y la Entrega 2 (E2). Para el detalle de cada cambio de diagramas y de modelo de datos, ver `02-bpmn.md` y `04-er-3fn.md`.

## Entrega 2 (noviembre de 2026)

### Agregado
- **Base de datos en SQLite** con 10 tablas en 3FN (`sql/schema.sql`), datos de prueba ficticios (`sql/datos_prueba.sql`) y consultas de negocio (`sql/consultas.sql`).
- **Modelo ER en 3FN** con cuatro entidades nuevas (Lote, DetallePedido, Publicacion y AlertaRemate) y la tabla de parámetros Configuracion (`04-er-3fn.md`).
- **Automatización de la alerta de remate** (`alerta_remate.py`), programada a diario con el Programador de tareas de Windows (`05-automatizacion.md`).
- **Aplicación web en Streamlit** (`E2/app/`) con acceso por clave y siete pantallas: Inventario, Registrar lote, Registrar venta, Entregas, Alertas, Publicar y Tablero.
- **Tablero de KPI** (K1 a K5) con fórmula, fuente, meta y responsable (`05-kpi-dashboard.md`).
- **Pruebas automáticas** con `unittest` (94 pruebas) y medición de tiempos de respuesta (`medir_tiempos.py`).
- **Documentos nuevos:** `04-sql-consultas.md`, `07-etica-ley-21719.md`, `08-supuestos.md`, `09-limitaciones.md` y este `CHANGELOG.md`.

### Cambiado
- **BPMN As-Is y To-Be corregidos** según la rúbrica de la E1: pools separados para los actores externos, caminos de excepción, verificación de pago, ciclo completo del remate y tareas tipificadas (`02-bpmn.md`).
- **Modelo de datos:** `Prenda` recibe `id_lote` y `costo`, y pierde `fecha_ingreso`; `Proveedor` se relaciona con `Lote`; `Pedido` pierde `canal_venta` y gana `fecha_entrega`; `Cliente` gana `comuna`.
- **Problema precisado** con las respuestas de la dueña: el stock se lleva en el catálogo de Instagram, el Excel es solo respaldo y organizar inventario y costos toma cerca de un día.
- **Automatización en Python** en vez de n8n, porque n8n no accede directamente a la base SQLite.
- **Fechas con hora local** (`'now', 'localtime'`) para que el conteo de días no cambie de día a las 21:00 (hora UTC).
- **Venta con clienta nueva:** la clienta y la venta se guardan en una sola transacción.
- **Tablero:** se retiraron los KPI K6 a K9 por no estar respaldados en el informe, para evitar discordancias.
- **README de la E2** reescrito con arquitectura, estructura, requisitos y puesta en marcha en cinco pasos.

### Pendiente o no implementado
- Descuento de bienvenida del 10 % y precio cobrado editable (`08-supuestos.md`, P2).
- Estado «reservada» para las reservas de hasta 15 días y distinción entre ventas por Instagram y por WhatsApp.
- Cambiar la clave de acceso o las metas de los KPI desde la app, y eliminar productos sin stock (`09-limitaciones.md`, L1 a L4).
- Efecto en la operación real no medido: todos los datos son de prueba.
- Procedimiento para ejercer derechos sobre datos personales y política de retención (`07-etica-ley-21719.md`).

## Entrega 1 (octubre de 2026)

- Caso Alta Facha, requerimientos (10 RF y 5 RNF con MoSCoW), BPMN As-Is y To-Be preliminares, ER preliminar, arquitectura y stack, plan de entrega y riesgos (`E1/docs/`).
