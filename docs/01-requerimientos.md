# C. Requerimientos

## C.1 Actores y roles

En el sistema intervienen cuatro actores, partiendo por la principal que es Belén, dueña y única operadora de Alta Facha, quien concentra todas las decisiones del negocio como lo son el registro de los lotes que recibe, las publicaciones a Instagram, atender a las clientas y coordinar los despachos. Por parte externa, está la clienta, que compra por mensaje directo con la dueña en Instagram. Por último, participa el distribuidor, que se encarga del despacho físico de las prendas; su rol es ejecutar la entrega y confirmarla, pero también es externo a la empresa.

Por otro lado, la propuesta de sistema que tenemos actúa como un actor interno que automatiza tareas que hoy se hacen a mano o no se hacen, como lo son generar las fichas de cada prenda, descontar el inventario cuando se concreta una venta, calcular el margen y lanzar alertas cuando una prenda lleva demasiados días sin venderse, además de poder llevar un registro de clientas para recopilar información deseable.

## C.2 Alcance

**Dentro del sistema (IN):**

- Registro de lotes de ropa con costo de adquisición
- Generación de ficha individual por prenda
- Control de inventario (disponible / vendido / entregado)
- Registro de ventas con precio de venta y cálculo automático de margen
- Registro y actualización de datos de clientes
- Generación de ficha de publicación (datos para subir a Instagram)
- Alerta automática de prendas sin venta superado un umbral de días configurado

**Fuera del sistema (OUT)** — cosas que el sistema podría abordar eventualmente, pero que para este caso no se consideran dado su complejidad de aplicación:

- Publicación directa en Instagram
- Gestión de pagos
- Comunicación con el cliente (sigue siendo por DM)
- Módulo contable o tributario

## C.3 Requisitos funcionales y no funcionales

Prioridad según MoSCoW: **M** = Must have · **S** = Should have · **C** = Could have

### Requisitos Funcionales

| ID | Requisito | Prioridad | Problema que resuelve |
|---|---|---|---|
| RF-01 | El sistema debe permitir registrar un lote de prendas indicando fecha de recepción y costo total del lote. | M | Belén no tiene registro de cuánto pagó por cada lote, imposibilitando calcular márgenes. |
| RF-02 | El sistema debe generar automáticamente una ficha individual por prenda al registrar un lote, incluyendo descripción, talla, precio sugerido y estado (disponible). | M | Las prendas se gestionan de memoria; no existe inventario estructurado. |
| RF-03 | El sistema debe registrar una venta asociando la prenda vendida, el precio cobrado, la fecha y el cliente. | M | Las ventas no quedan registradas, lo que impide analizar ingresos o detectar errores. |
| RF-04 | El sistema debe calcular y almacenar automáticamente el margen de ganancia por prenda al momento de registrar la venta. | M | Belén desconoce la rentabilidad real de cada transacción. |
| RF-05 | El sistema debe registrar o actualizar los datos del cliente (nombre, contacto) en cada venta. | M | No existe historial de clientes; se pierde la posibilidad de fidelización. |
| RF-06 | El sistema debe generar una ficha de publicación por prenda con la información necesaria para subir a Instagram. | S | El proceso de publicación es manual y repetitivo; una ficha estructurada lo agiliza. |
| RF-07 | El sistema debe detectar prendas que superen un umbral configurable de días sin venta y generar una alerta de remate. | S | Prendas con bajo movimiento no generan ninguna señal, ocupando inventario sin producir ingresos. |
| RF-08 | El sistema debe permitir marcar una prenda como entregada y registrar la fecha de entrega al confirmar el despacho. | M | El cierre del proceso (entrega) no queda registrado; el inventario puede quedar inconsistente. |
| RF-09 | El sistema debe mostrar un resumen de inventario con prendas disponibles, vendidas y entregadas. | S | Belén no tiene visibilidad del estado actual de su stock en ningún momento. |
| RF-10 | El sistema debe permitir configurar el umbral de días sin venta que activa la alerta de remate. | C | El umbral óptimo depende del contexto del negocio y puede variar en el tiempo. |

### Requisitos No Funcionales

| ID | Requisito | Prioridad | Justificación |
|---|---|---|---|
| RNF-01 | La interfaz debe ser operable desde un smartphone sin capacitación técnica previa. | M | Belén es la única usuaria y gestiona el negocio desde su teléfono mientras coordina entregas o atiende clientes. |
| RNF-02 | El sistema debe estar disponible al menos el 95% del tiempo en horario de operación (09:00–22:00). | M | Las ventas ocurren en cualquier momento del día vía Instagram; una caída implica pérdida de registro de ventas. |
| RNF-03 | El acceso al sistema debe requerir autenticación con contraseña. | S | Los datos de clientes y márgenes son información sensible del negocio. |
| RNF-04 | El tiempo de respuesta de cualquier operación de registro o consulta debe ser inferior a 3 segundos. | S | Una herramienta lenta será abandonada por Belén en favor de su método actual. |
| RNF-05 | El sistema debe poder ser mantenido o extendido por un desarrollador sin conocimiento previo del proyecto, dado un README adecuado. | C | La sostenibilidad del sistema a largo plazo requiere que no dependa exclusivamente de su desarrollador original. |
