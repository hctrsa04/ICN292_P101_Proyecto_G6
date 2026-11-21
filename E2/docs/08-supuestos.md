# Supuestos y decisiones del SIG

> Las rutas de código de este documento son relativas a `E2/app/`.

Registro vivo. Si una regla cambia, se anota aquí qué cambió, quién lo decidió y qué archivos se tocaron.

Última actualización: 21-nov-2026.

## Reglas aclaradas por el equipo

Estas reglas vienen de Iván, responsable del BPMN y apoyo del modelo SQL.

| # | Regla | Qué implica |
|---|---|---|
| R1 | **Cada prenda tiene su costo individual.** El lote guarda su costo total por separado. El costo del lote **no** se reparte parejo entre las prendas. | `registrar_lote` recibe el costo de cada prenda. Calza con el esquema actual (`Prenda.costo`, `Lote.costo_total`) sin cambios. La validación entre ambos montos está pendiente (P1). |
| R2 | **Stock comercializable = prendas en estado `disponible` y `en_remate`.** Las consultas de detalle muestran el estado individual; los totales de stock suman ambos estados. | Coincide con `stock_disponible()` y con las consultas 1, 1b y 1c de `sql/consultas.sql`. La alerta de remate (`alerta_remate.py`) y la consulta 3 siguen evaluando solo `disponible`, porque una prenda en remate ya tuvo su alerta atendida. |
| R3 | **Las clientas se identifican por `id_cliente`.** El contacto (teléfono o Instagram) no es único y no se impone unicidad. | En la venta se elige una clienta existente o se registra una nueva. Si es nueva, la clienta y la venta se guardan en **una misma transacción**. |
| R4 | **Precio de venta: se mantiene el comportamiento actual.** `registrar_venta()` cobra `precio_venta`, o `precio_remate` si la prenda está en remate, y lo guarda como `precio_final`. | No se modifica `registrar_venta()` para permitir precios editables (ver P2). |

## Decisiones pendientes

Mientras no se resuelvan, se mantiene el comportamiento actual.

| # | Tema | Qué hace hoy el código | Quién decide |
|---|---|---|---|
| P1 | Relación entre la suma de los costos de las prendas y `Lote.costo_total` (¿deben ser iguales?, ¿se avisa si difieren?) | No hay validación | Equipo (Iván) |
| P2 | Precio cobrado distinto del precio publicado | No se permite. El seed tiene un caso así (prenda 4: publicada a 18.000, cobrada a 16.000) que la app no puede reproducir. | Mejora pendiente de validación |
| P3 | Fecha base de los "días sin venta" | Desde `Lote.fecha_recepcion` | Belén |
| P4 | Borde del umbral: con umbral 30, ¿alertar el día 30 o el 31? | Compara días con decimales (`> umbral`), así que alerta el día 30 | Belén |
| P5 | Devoluciones y cancelaciones | No existen: una prenda se vende una sola vez | Belén |
| P6 | Definición final y metas de los KPI | Las consultas actuales apoyan la operación del BPMN to-be y **no** se dan por KPI definitivos. Las metas se muestran como "por definir", salvo K4: meta ≥ 2,0 veces la inversión por lote (Belén, respuesta 2 del cuestionario, recogida en el informe E2). K6 a K9 se retiraron el 21-nov por no estar en el informe. | Ricardo con Belén |
