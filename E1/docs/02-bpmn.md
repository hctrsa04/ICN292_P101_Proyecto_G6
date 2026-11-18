# D. Procesos BPMN

## D.1 BPMN As-Is

El proceso actual se modela con un pool para Alta Facha y pools colapsados para los participantes externos: Clienta, Mayorista, Mercado Pago y Distribuidor (agencia de delivery), que se comunican con Alta Facha mediante flujos de mensaje. Dentro de Alta Facha no existe un carril de sistema ni otros cargos, ya que toda la gestión la realiza manualmente su dueña, Belén.

El flujo comienza con la necesidad de reponer stock. Belén compra un lote de ropa al mayorista y, una vez recibido en su departamento, plancha las prendas, las fotografía y las publica manualmente en Instagram. El proceso queda en espera hasta que una clienta consulta por mensaje directo. En ese momento, Belén revisa la disponibilidad de la prenda sin apoyo de ningún registro, ya que no lleva control de inventario y todo se hace "al ojo". Si la prenda no está disponible, se informa a la clienta y la venta no se concreta. Si está disponible, se le confirma con el precio publicado, que ya incluye el costo de envío, y se espera su confirmación de compra; si no responde en un plazo determinado, la venta tampoco se concreta.

Confirmada la compra y verificado el pago en Mercado Pago, Belén decide el tipo de entrega: si la clienta está cerca de Las Condes, la entrega ella misma; en caso contrario, coordina el despacho con una agencia de delivery. Finalmente, una vez entregada la prenda, registra la venta y calcula el margen en una planilla Excel.

De forma independiente, al terminar cada temporada Belén identifica a ojo las prendas que no se vendieron, fija un precio de remate y las vuelve a publicar.

En el diagrama se marcan con anotaciones los principales puntos de dolor:

- La falta de control de inventario.
- La publicación manual, que es la tarea que más tiempo consume.
- La ausencia de una base de datos de clientas, cuyos datos quedan solo en los mensajes directos.
- El registro tardío de la venta, que ocurre después de la entrega.
- La falta de datos sobre la antigüedad de cada prenda al momento de decidir un remate.

![BPMN As-Is](../assets/BPMN%20Alta%20Facha%20As-IS%28corregido%29.jpeg)

## D.2 BPMN To-Be con la intervención del SIG

El proceso propuesto mantiene los mismos participantes del As-Is, pero divide el pool de Alta Facha en dos carriles: Belén y el Sistema de Información de Gestión (SIG), compuesto por una aplicación en Streamlit, una base de datos SQLite y automatizaciones en n8n. Las tareas se tipifican según quién las ejecuta: tareas de usuario cuando Belén opera el sistema, tareas de servicio cuando el SIG actúa de forma automática y tareas manuales para el trabajo físico.

El planchado y la fotografía se mantienen como tareas manuales. Luego, Belén registra el lote y sus prendas en el sistema, indicando el costo y el precio de venta de cada una, y el SIG genera automáticamente la ficha de cada prenda y su ficha de publicación, con la cual Belén publica en Instagram.

Cuando llega una consulta, Belén verifica la disponibilidad en el SIG en lugar de hacerlo de memoria. La venta se registra en el sistema apenas se verifica el pago, y no después de la entrega como ocurría antes. Al registrarla, el SIG ejecuta en paralelo, mediante un gateway AND, tres acciones: descontar la prenda del inventario, calcular y registrar el margen, y registrar o actualizar los datos de la clienta. Después de la entrega, Belén marca la prenda como entregada y el sistema registra la fecha, cerrando el ciclo de la venta.

De forma independiente al flujo principal, un evento temporizador activa periódicamente, mediante n8n, la evaluación de los días sin venta de cada prenda, según el umbral y la frecuencia que configura Belén. Si hay prendas sobre el umbral, un gateway XOR genera una alerta de remate. Belén define el margen que está dispuesta a obtener, el SIG calcula el precio de remate y ella publica las prendas.

![BPMN To-Be](../assets/BPMN%20Alta%20Facha%20To-Be%28corregido%29.jpeg)

## D.3 Mejoras introducidas por el SIG

**¿Qué se automatiza?**

- **Fichas por prenda y de publicación:** antes cada publicación se preparaba completamente a mano y era la tarea que más tiempo consumía; ahora el SIG entrega los datos de cada prenda listos para publicar. *KPI: tiempo promedio de publicación por lote (antes vs. después).*
- **Cálculo de margen y del precio de remate:** antes se hacía con cálculos manuales en Excel después de la entrega; ahora es automático al registrar la venta o al definir el margen de remate. *KPI: margen real por prenda y por lote, comparado con la meta de Belén de obtener al menos el doble de lo invertido.*

**¿Qué se controla?**

- **Estado de cada prenda** (disponible, en remate, vendida o entregada): queda registrado en el sistema, lo que resuelve la falta de control de inventario y elimina la revisión "al ojo". *KPI: porcentaje de consultas respondidas con disponibilidad errónea (meta: 0 %).*
- **Registro de clientas:** pasa de ser inexistente a actualizarse en cada venta, permitiendo identificar clientas frecuentes. *KPI: porcentaje de ventas con clienta registrada y tasa de clientas recurrentes.*
- **Registro de ventas:** ocurre al confirmarse el pago y no después de la entrega, lo que reduce el riesgo de omitir una venta. *KPI: porcentaje de ventas registradas el mismo día de su confirmación.*

**¿Qué se mide?**

- **Antigüedad de cada prenda en inventario:** antes el remate se decidía a ojo al final de la temporada; ahora la alerta se basa en los días sin venta. *KPI: días promedio hasta la venta por tipo de prenda y porcentaje de prendas que terminan en remate.*
- **Historial de ventas por clienta y por tipo de prenda:** permite saber qué prendas rotan más rápido y orientar las próximas compras de lotes.
