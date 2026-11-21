# Procesos BPMN (versión final de la Entrega 2)

Esta versión reemplaza a la de la Entrega 1 (`E1/docs/02-bpmn.md`) después de corregir los diagramas según la retroalimentación de la rúbrica. Los archivos están en `E2/assets/`:

- `BPMN Alta Facha As-IS(corregido).jpeg`
- `BPMN Alta Facha To-Be(corregido).jpeg.jpg`

## 1. BPMN As-Is final

![BPMN As-Is corregido](../assets/BPMN%20Alta%20Facha%20As-IS(corregido).jpeg)

**Cómo leerlo.** Belén es el único participante interno de Alta Facha. Compra el lote al mayorista, lo plancha y fotografía, publica en Instagram y atiende por mensaje directo la consulta de la clienta. Revisa la disponibilidad a mano y, si hay stock, confirma a la clienta, verifica el pago en Mercado Pago y entrega en persona o coordina el despacho con el distribuidor, según la cercanía a Las Condes. Cierra anotando la venta y calculando el margen en la planilla Excel (representada como almacén de datos).

- Hay dos finales de excepción: sin stock y sin respuesta de la clienta (evento temporizador).
- Hay un flujo independiente de remate al final de la temporada, en que las prendas sin vender se identifican «al ojo».
- Mayorista, Clienta, Mercado Pago y Distribuidor son pools externos, unidos al pool de Alta Facha por flujos de mensaje rotulados.

## 2. BPMN To-Be final

![BPMN To-Be corregido](../assets/BPMN%20Alta%20Facha%20To-Be(corregido).jpeg.jpg)

**Cómo leerlo.** El pool de Alta Facha tiene dos carriles: **Belén** (tareas manuales y de usuario) y **SIG** (tareas de servicio sobre SQLite y Python).

1. **Al recibir el lote**, Belén lo registra con el costo y el precio de cada prenda. El SIG genera las fichas de prenda y de publicación.
2. **La consulta de la clienta** se responde consultando la disponibilidad en el SIG. Si no hay stock, se informa a la clienta.
3. **Tras verificar el pago**, Belén registra la venta. El SIG ejecuta en paralelo (gateway AND) tres acciones: descuenta la prenda del inventario, calcula y guarda el margen, y registra o actualiza a la clienta.
4. **La entrega** la hace Belén en persona o por distribuidor. Marca la prenda como entregada y el SIG registra la fecha de entrega.
5. **La revisión periódica** (evento temporizador, carril del SIG) evalúa los días sin venta de cada prenda. Si hay prendas sobre el umbral (gateway XOR), genera la alerta de remate. Belén define el margen de remate, el SIG calcula el precio y Belén publica las prendas en remate.

## 3. Qué cambió respecto de la E1

| Elemento | E1 | E2 | Motivo |
|---|---|---|---|
| As-Is: participantes | Un pool con tres carriles: Belén, Cliente y Distribuidor | Pool de Alta Facha y pools separados de Clienta, Mayorista, Mercado Pago y Distribuidor, unidos por flujos de mensaje rotulados | Notación (8/16) y actores externos (12/16) |
| As-Is: excepciones | Un solo fin, por falta de stock | Fin sin stock y fin sin respuesta de la clienta (temporizador), ambos con nombre de estado | Caminos de excepción (27/36) |
| As-Is: pago y registro | El pago no aparece; la venta se anota en un «Excel manual» | Se verifica el pago en Mercado Pago, se decide la entrega según la cercanía a Las Condes y se registran venta y margen en el Excel | Incidencias y registros manuales (27/36) |
| As-Is: remate | No aparece | Flujo independiente de fin de temporada: identificar prendas sin vender «al ojo», fijar el precio de remate y publicarlas | Punto de dolor real: antigüedad del stock |
| To-Be: estructura | Un pool con cuatro carriles (Distribuidor, Belén, Sistema y Clienta); tareas sin tipificar | Pool de Alta Facha con dos carriles (Belén y SIG), pools externos separados, tareas de usuario, de servicio y manuales, y finales con nombre | Notación y consistencia de participantes |
| To-Be: consulta de disponibilidad | La venta se registra sin revisar el inventario en el SIG | «Consultar disponibilidad en SIG» lee la base de datos y, si no hay stock, se informa a la clienta | Punto de dolor del As-Is: falta de control de inventario |
| To-Be: registro del lote | «Registrar lote en sistema» al inicio y «Subir foto al sistema» antes de publicar | Tras planchar y fotografiar, «Registrar lote y prendas (costo y precio)»; el SIG genera las fichas | Costo por prenda para calcular el margen |
| To-Be: venta | «Registrar venta en sistema» al recibir el pedido | Se verifica el pago y luego se registra la venta; se mantienen las tres acciones en paralelo | Evita el registro tardío del As-Is |
| To-Be: entrega | Belén marca la prenda como entregada | Además, el SIG registra la fecha de entrega | RF-08 |
| To-Be: remate | El temporizador genera la alerta y el flujo termina | Tras la alerta, Belén define el margen de remate, el SIG calcula el precio y Belén publica | Cierra el ciclo del remate y lo alinea con `AlertaRemate` y `Prenda.precio_remate` |

## 4. Qué mejora el SIG

**¿Qué se automatiza?** Las fichas por prenda y de publicación, el descuento de inventario y el cálculo del margen al vender, y la revisión periódica de antigüedad con su alerta de remate.

**¿Qué se controla?** El estado de cada prenda (disponible, en remate, vendida o entregada) queda registrado en el sistema, y el SIG consulta la disponibilidad antes de confirmar una venta, para no vender una prenda ya vendida.

**¿Qué se mide?** El margen por prenda y por lote, la recuperación de la inversión, la antigüedad del stock y las ventas por mes (KPI K1 a K5, ver `05-kpi-dashboard.md`).

## 5. Dónde se implementa cada tarea del To-Be

| Tarea del To-Be | Implementación en la app (`E2/app/`) |
|---|---|
| Registrar lote y prendas; generar fichas por prenda | Pantalla **Registrar lote** (`registrar_lote()`) |
| Generar ficha de publicación | Pantalla **Publicar** (`generar_ficha_publicacion()`) |
| Consultar disponibilidad en SIG | Pantalla **Inventario** y lista de prendas de **Registrar venta** |
| Registrar venta; descontar prenda; calcular margen; registrar clienta | Pantalla **Registrar venta** (`registrar_venta()`, una sola transacción) |
| Marcar prenda como entregada | Pantalla **Entregas** (`marcar_entregado()`) |
| Evaluar días sin venta y generar alerta de remate | `alerta_remate.py` (tarea diaria) y botón «Revisar ahora» de **Alertas** |
| Definir margen y calcular precio de remate | Pantalla **Alertas** (`atender_alerta()`) |

La trazabilidad completa entre tareas y tablas (crear, leer, actualizar) está en `04-er-3fn.md`.
