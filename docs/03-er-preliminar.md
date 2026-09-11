# Diagrama Entidad-Relación (Preliminar)
## 1. Entidades y atributos

A partir de la entrevista con la dueña de la PYME se pudo reconocer que los actores principales dentro del proceso productivo (con sus respectivos atributos) son: 

| Entidad | Atributos |
|-|-|
| Prenda | id_prenda, tipo, talla, fecha_ingreso, precio_compra, precio_venta, precio_remate, estado |
| Proveedor | id_proveedor, nombre |
| Distribuidor | id_distribuidor, nombre |
| Cliente | id_cliente, nombre, contacto |
| Pedido | id_pedido, id_cliente (FK), fecha, canal_venta, tipo_entrega, id_distribuidor (FK, si aplica)|

Lo que en palabras sería:

- Prenda: Un código identificador para cada prenda asociado a características tales como el tipo de prenda, su talla, fecha de ingreso al inventario, el precio al que se adquirió, el precio al cual se desea ofertar y un precio en caso de que la prenda se remate.
- Proveedor: Un código identificador para cada proveedor que me indica el nombre del mismo. No se cuenta con mayor información sobre proveedores.
- Distribuidor: Un código identificador para cada distribuidor que nos indica el nombre. No se maneja mayor información sobre distribuidores. 
- Cliente: Un código identificador para cada cliente que entrega el nombre y contacto del usuario.
- Pedido: Un código identificador para cada pedido, asociado con un cliente que solicitó uno o muchos productos en cierta fecha, en el canal de venta correspondiente y que dependiendo de su ubicación geográfica en la ciudad o alrededores se le asigna un envío por parte de la propia dueña o una agencia especialista.

## 2. Relación entre entidades (Cardinalidad)

No solo es importante reconocer las entidades que participan de este proceso, tampoco basta con destacar sus atributos relevantes, sino que también es de suma importancia reconocer cómo es que se relacionan entre sí, si existe algún tipo de relación. Por lo mismo, a continuación se reconocerá la cardinalidad en la interacción entre entidades:

- Proveedor-Prenda (1,N): Decimos que un proveedor abastece de múltiples prendas, pero que cada prenda proviene de un único proveedor. Esto es coherente con el tipo de negocio que maneja la PYME, puesto que la dueña declara comprar sus insumos a mayoristas en fardos de ropa, lo cual sugiere (y no hay declaraciones que lo contradigan) que efectivamente una prenda proviene de un único proveedor.
- Pedido-Prenda (1,N): Un pedido puede estar constituido por diversas prendas, pero cada prenda pertenece a un único pedido. Lo anterior se sustenta en el mismo modo de operación de la empresa, específicamente en el abastecimiento de la misma, donde se comprende que prácticamente cada prenda es de existencia única en el catálogo que se maneja periodo a periodo.
- Cliente-Pedido (1,N): Desde aquí se entiende que un cliente puede realizar más de un pedido, pero que cada pedido pertenece a un único cliente.
- Distribuidor (0,1) - Pedido (1,N): Esta resulta ser la relación más "delicada" de entender, puesto que se sostiene únicamente de la declaraciones de Belén en la reunión que se realizó. Dentro de esta reunión, se nos indica que ella terceriza el envío de sus pedidos a sus clientes, pero existe una excepción dependiendo de la ubicación de su cliente:
  1. Si el cliente vive en Las Condes, puede darse un envío ejecutado por la propia dueña.
  2. Dado otro caso, la entrega del pedido será confiada a una empresa de servicios de paquetería.
- Con esto en mente, se entiende entonces que un distribuidor puede estar a cargo de más de un pedido, sin embargo, un pedido puede estar a cargo de una única o ninguna empresa de repartos.

## 3. Justificación con el modelo BPMN

Esta descripción del proceso To-Be respalda directamente el diseño del ER preliminar:

- La generación de **fichas individuales por prenda** al ingresar el lote justifica que *Prenda* sea una entidad con identidad propia (*id_prenda*), y no simplemente una cantidad dentro de un lote genérico.
- El **registro de cliente** en paralelo al registrar la venta confirma que *Cliente* debe capturarse en el momento del *Pedido*, coherente con la FK *id_cliente* en *Pedido*.
- El **descuento de inventario** automático depende del atributo *estado* de *Prenda*, que permite distinguir entre disponible/vendida/rematada.
- La **alerta de remate** generada por el evento temporizador se apoya en poder calcular días sin venta por prenda, esto sugiere que *Prenda* necesitaría un atributo de fecha (ej. *fecha_ingreso*) para que el sistema pueda calcular cuántos días lleva sin venderse.
