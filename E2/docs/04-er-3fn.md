# E. Diagrama Entidad-Relación (Preliminar)

![Diagrama ER](assets/ER_3FN.png)

*Diagrama ER*

## E.1 Entidades y atributos

A partir de la entrevista con la dueña de la PYME y del proceso To-Be, se identificaron las siguientes entidades:

| Entidad | Atributos |
| --- | --- |
| Proveedor | **id_proveedor**, nombre |
| Lote | **id_lote**, id_proveedor (FK), fecha_recepcion, costo_total, cantidad_prendas |
| Prenda | **id_prenda**, id_lote (FK), tipo, talla, costo, precio_venta, precio_remate, estado |
| Publicacion | **id_publicacion**, id_prenda (FK), fecha_publicacion, descripcion, foto |
| AlertaRemate | **id_alerta**, id_prenda (FK), fecha_alerta, dias_sin_venta, margen_remate, estado_alerta |
| Cliente | **id_cliente**, nombre, contacto, comuna |
| Pedido | **id_pedido**, id_cliente (FK), id_distribuidor (FK, nulo si la entrega es propia), fecha_venta, tipo_entrega, fecha_entrega |
| DetallePedido | **id_pedido (FK)**, **id_prenda (FK, único)**, precio_final, margen |
| Distribuidor | **id_distribuidor**, nombre |

*En negrita la clave primaria (PK).*

En palabras:

- **Proveedor**: mayorista al que Belén le compra los fardos de ropa. Solo se maneja su nombre.

- **Lote**: cada compra de un fardo, con su fecha de recepción, costo total y cantidad de prendas. Permite calcular el margen por lote.

- **Prenda**: cada prenda individual del lote. Belén ingresa su costo y precio de venta. El precio de remate se calcula a partir del margen que ella define. El estado puede ser *disponible*, *en remate*, *vendida* o *entregada*.

- **Publicacion**: ficha de publicación que genera el sistema para subir a Instagram. Una prenda puede publicarse más de una vez (por ejemplo, al rematarse).

- **AlertaRemate**: alerta que genera la automatización cuando una prenda supera el umbral de días sin venta. Guarda el margen de remate que define Belén.

- **Cliente**: clienta que compra. Se guardan solo los datos necesarios para la venta y la entrega (nombre, contacto y comuna).

- **Pedido**: venta confirmada a una clienta. Indica si la entrega fue propia o por distribuidor y la fecha en que se entregó.

- **DetallePedido**: prendas incluidas en cada pedido, con el precio final cobrado y el margen obtenido.

- **Distribuidor**: agencia de delivery a la que se le encarga el despacho cuando la entrega no es cercana a Las Condes.

## E.2 Relaciones entre entidades (cardinalidad)

- **Proveedor (1) – Lote (1,N)**: un proveedor puede abastecer varios lotes, y cada lote proviene de un único proveedor. La relación es con el lote y no con la prenda, porque Belén compra fardos completos y no prendas sueltas.

- **Lote (1) – Prenda (1,N)**: un lote contiene una o muchas prendas, y cada prenda pertenece a un único lote. Así se puede rastrear el origen y el costo de cada prenda.

- **Prenda (1) – Publicacion (0,N)**: una prenda puede no estar publicada todavía o tener varias publicaciones. Cada publicación corresponde a una sola prenda.

- **Prenda (1) – AlertaRemate (0,N)**: una prenda puede no generar alertas o generar varias si sigue sin venderse.

- **Prenda (1) – DetallePedido (0,1)**: como cada prenda es única, se vende como máximo una vez. Una prenda que aún no se vende no tiene detalle de pedido.

- **Pedido (1) – DetallePedido (1,N)**: un pedido incluye una o varias prendas.

- **Cliente (1) – Pedido (1,N)**: una clienta puede realizar varios pedidos, y cada pedido pertenece a una sola clienta. La clienta se registra al momento de la venta, por lo que siempre tiene al menos un pedido.

- **Distribuidor (0,1) – Pedido (0,N)**: un pedido es despachado por un distribuidor o por ninguno (cuando Belén entrega en persona, por cercanía a Las Condes). Un distribuidor puede tener varios pedidos a cargo.

Cambios respecto de la versión anterior:

- Se agregó **Lote**, ya que el proveedor entrega fardos y el costo se conoce a nivel de lote.

- Se agregó **DetallePedido** para resolver la relación entre Pedido y Prenda y guardar el precio final cobrado y el margen de cada venta.

- La relación Pedido–Prenda pasó a ser (0,1) desde la prenda, porque una prenda no vendida no tiene pedido.

- Se agregaron **Publicacion** y **AlertaRemate**, que aparecen en el proceso To-Be y no estaban en el modelo.

- Se eliminó *canal_venta*, porque todas las ventas se realizan por Instagram.

- Se eliminó *fecha_ingreso* de Prenda, porque se obtiene desde el lote, y se unificaron los estados de la prenda con los del BPMN.

## E.3 Trazabilidad BPMN To-Be → entidades (CRUD)

C = crea, R = lee, U = actualiza. PV = Proveedor, LO = Lote, PR = Prenda, PU = Publicacion, AR = AlertaRemate, CL = Cliente, PE = Pedido, DP = DetallePedido, DI = Distribuidor.

| Tarea del BPMN To-Be | PV | LO | PR | PU | AR | CL | PE | DP | DI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Registrar lote y prendas | R | C | C |  |  |  |  |  |  |
| Generar fichas por prenda |  | R | U |  |  |  |  |  |  |
| Generar ficha de publicación |  |  | R | C |  |  |  |  |  |
| Consultar disponibilidad en SIG |  |  | R |  |  |  |  |  |  |
| Registrar venta en SIG |  |  | R |  |  |  | C | C |  |
| Descontar prenda del inventario |  |  | U |  |  |  |  |  |  |
| Calcular y registrar margen |  |  | R |  |  |  |  | U |  |
| Registrar o actualizar clienta |  |  |  |  |  | C/U |  |  |  |
| Coordinar despacho con distribuidor |  |  |  |  |  |  | U |  | R |
| Marcar prenda como entregada |  |  | U |  |  |  | U |  |  |
| Evaluar días sin venta por prenda |  |  | R | R |  |  |  |  |  |
| Generar alerta de remate |  |  |  |  | C |  |  |  |  |
| Definir margen de remate |  |  |  |  | U |  |  |  |  |
| Calcular precio de remate |  |  | U |  | R |  |  |  |  |

## E.4 Justificación con el modelo BPMN

- Al **registrar el lote** se crean el Lote y sus Prendas, por lo que el costo de cada prenda queda asociado a su lote y se puede calcular el margen por prenda y por lote.

- La **ficha de publicación** se guarda en Publicacion. Su fecha permite calcular cuántos días lleva una prenda publicada sin venderse. Sin embargo, las alertas de remate consideran un plazo de días a partir de la **fecha de recepción** del lote.

- Al **registrar la venta**, el sistema ejecuta en paralelo el descuento de inventario (estado de Prenda), el cálculo del margen (DetallePedido) y el registro de la clienta (Cliente), tal como en el gateway AND del To-Be.

- La **decisión de entrega** queda registrada en Pedido mediante *tipo_entrega* e *id_distribuidor*, que queda nulo cuando Belén entrega en persona.

- La **alerta de remate** se apoya en las fechas de Publicacion y en el estado de Prenda. El margen que define Belén se guarda en AlertaRemate y con él se calcula el *precio_remate* de la prenda.

- El umbral y la frecuencia de revisión los configura Belén y se guardan como parámetros del sistema, no como una entidad del modelo.

## E.5 Normalización hasta Tercera Forma Normal (3FN)

Para verificar que el modelo no tenga redundancias ni anomalías de inserción, actualización o eliminación, se normaliza partiendo del registro de una venta tal como se anotaría hoy en una sola planilla. Notación: la clave primaria va <ins>subrayada</ins>, las claves foráneas se marcan con *(FK)* y los grupos repetitivos se escriben entre { }.

### Paso 0: Forma no normalizada (0FN)

Registro de una venta en una sola fila, donde un pedido lleva una o varias prendas:

VENTA (<ins>id_pedido</ins>, fecha_venta, nombre_cliente, contacto, comuna, tipo_entrega, nombre_distribuidor, fecha_entrega, { id_prenda, tipo, talla, costo, precio_venta, precio_remate, estado, precio_final, margen, id_lote, fecha_recepcion, costo_total, cantidad_prendas, nombre_proveedor })

**Problema:** existe un grupo repetitivo (las prendas del pedido), por lo que una misma celda guarda varios valores.

### Paso 1: Primera Forma Normal (1FN)

**Regla:** todos los atributos deben ser atómicos y no deben existir grupos repetitivos.

Se separa el grupo repetitivo en una fila por cada prenda de cada pedido. La clave pasa a ser compuesta (id_pedido, id_prenda):

VENTA_1FN (<ins>id_pedido</ins>, <ins>id_prenda</ins>, fecha_venta, nombre_cliente, contacto, comuna, tipo_entrega, nombre_distribuidor, fecha_entrega, tipo, talla, costo, precio_venta, precio_remate, estado, id_lote, fecha_recepcion, costo_total, cantidad_prendas, nombre_proveedor, precio_final, margen)

**Problema:** hay redundancia. Si un pedido tiene tres prendas, los datos del pedido y de la clienta se repiten tres veces, y los datos del lote se repiten en cada prenda del mismo lote.

### Paso 2: Segunda Forma Normal (2FN)

**Regla:** estar en 1FN y que ningún atributo no clave dependa solo de una parte de la clave compuesta.

Dependencias funcionales identificadas:

- id_pedido → fecha_venta, nombre_cliente, contacto, comuna, tipo_entrega, nombre_distribuidor, fecha_entrega *(dependencia parcial)*.

- id_prenda → tipo, talla, costo, precio_venta, precio_remate, estado, id_lote, fecha_recepcion, costo_total, cantidad_prendas, nombre_proveedor *(dependencia parcial)*.

- (id_pedido, id_prenda) → precio_final, margen *(dependencia completa)*.

Se separa cada grupo en su propia tabla:

PEDIDO (<ins>id_pedido</ins>, fecha_venta, nombre_cliente, contacto, comuna, tipo_entrega, nombre_distribuidor, fecha_entrega)

PRENDA (<ins>id_prenda</ins>, tipo, talla, costo, precio_venta, precio_remate, estado, id_lote, fecha_recepcion, costo_total, cantidad_prendas, nombre_proveedor)

DETALLE_PEDIDO (<ins>id_pedido</ins>, <ins>id_prenda</ins> *(FK)*, precio_final, margen)

**Problema:** aún existen dependencias transitivas. En PEDIDO, los datos de la clienta dependen de la clienta y no del pedido. En PRENDA, los datos del lote dependen del lote y no de la prenda.

### Paso 3: Tercera Forma Normal (3FN)

**Regla:** estar en 2FN y que ningún atributo no clave dependa de otro atributo no clave.

Dependencias transitivas identificadas:

- En PEDIDO: id_pedido → clienta → nombre, contacto, comuna. Se crea la tabla CLIENTE con clave id_cliente, y PEDIDO conserva solo la FK.

- En PRENDA: id_prenda → id_lote → fecha_recepcion, costo_total, cantidad_prendas, nombre_proveedor. Se crea la tabla LOTE, y PRENDA conserva solo la FK id_lote.

Resultado en 3FN:

CLIENTE (<ins>id_cliente</ins>, nombre, contacto, comuna)

DISTRIBUIDOR (<ins>id_distribuidor</ins>, nombre)

PEDIDO (<ins>id_pedido</ins>, id_cliente *(FK)*, id_distribuidor *(FK, nulo si la entrega es propia)*, fecha_venta, tipo_entrega, fecha_entrega)

PROVEEDOR (<ins>id_proveedor</ins>, nombre)

LOTE (<ins>id_lote</ins>, id_proveedor *(FK)*, fecha_recepcion, costo_total, cantidad_prendas)

PRENDA (<ins>id_prenda</ins>, id_lote *(FK)*, tipo, talla, costo, precio_venta, precio_remate, estado)

DETALLE_PEDIDO (<ins>id_pedido</ins>, <ins>id_prenda</ins> *(FK)*, precio_final, margen)

Las entidades PUBLICACION y ALERTA_REMATE ya cumplen 3FN, porque sus atributos dependen solo de su propia clave y se relacionan con PRENDA mediante id_prenda. Con esto, el resultado coincide con el modelo ER presentado en E.1.

### Observaciones

- **Proveedor y Distribuidor:** como solo guardan el nombre, su separación no es una exigencia estricta de la 3FN, sino una decisión de diseño para evitar nombres escritos de distintas formas y permitir agregar más datos en el futuro.

- **Margen:** es un atributo derivado (precio_final − costo). Se almacena porque así lo exige RF-04 y porque deja un registro histórico del margen de cada venta.

- **Clave de DETALLE_PEDIDO:** como cada prenda es única y se vende una sola vez, id_prenda también identifica la fila por sí sola (es clave candidata, por eso se marca como único). Se mantiene la clave compuesta por coherencia con el modelo ER.
