# Diagrama Entidad-Relación (Preliminar)

| Entidad | Atributos |
|-|-|
| Prenda | id_prenda, tipo, talla, temporada, precio_compra, precio_venta, precio_remate, estado |
| Proveedor | id_proveedor, nombre |
| Distribuidor | id_distribuidor, nombre, tipo_envio |
| Cliente | id_cliente, nombre, contacto |
| Pedido | id_pedido, id_cliente (FK), fecha, canal_venta, tipo_entrega, id_distribuidor (FK, si aplica)|
