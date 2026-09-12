# D. Procesos BPMN

## D.1 BPMN As-Is

El proceso actual se modela con tres participantes correspondientes a Alta Facha, Cliente y Distribuidor. No existe ningún carril de sistema o de cargo específico dentro de la empresa porque todo es gestión manual de la dueña.

El flujo inicia con la recepción de un lote, se planchan las prendas, se toman fotografías y se publica manualmente en Instagram. El proceso queda en espera hasta que el cliente contacta por DM, Belén atiende la consulta, acuerda la venta, coordina el despacho con el distribuidor y, al confirmar entrega, registra la venta en una planilla Excel.

![BPMN As-Is](../assets/BPMN%20Alta%20Facha%20As-Is.png)

## D.2 BPMN To-Be con la intervención del SIG

El flujo To-Be conserva ciertas tareas de Belén e intercala tareas automáticas del Sistema de Información de Gestión (SIG) en los puntos donde antes no existía registro. Por ejemplo, al ingresar el lote el SI genera fichas individuales por prenda; al publicar, genera la ficha de publicación; al registrar la venta, el SIG ejecuta en paralelo tres acciones —descuento de inventario, cálculo de margen y registro de cliente— mediante un gateway AND. De forma independiente al flujo principal, un evento temporizador periódico activa la evaluación de días sin venta, que mediante un gateway XOR genera o no una alerta de remate.

![BPMN To-Be](../assets/BPMN%20Alta%20Facha%20To-Be.png)

## D.3 Mejoras introducidas por el SIG

**¿Qué se automatiza?**
La generación de fichas por prenda y por publicación, el cálculo de márgenes y el descuento de inventario al momento de la venta, tareas que antes dependían totalmente del registro manual de Belén.

**¿Qué se controla?**
El estado de cada prenda (disponible / vendida / entregada) queda trazado en el sistema, eliminando la posibilidad de vender una prenda ya despachada o de perder el registro de una transacción. El registro de clientes pasa de ser inexistente a mantenerse actualizado en cada venta, permitiendo identificar clientes frecuentes, productos populares y otros análisis que antes no se podían realizar por falta de datos.

**¿Qué se mide?**
El margen de ganancia por prenda y por lote, la antigüedad de las prendas en inventario y el historial de ventas por cliente. Con esto se habilitan decisiones basadas en información que hoy Alta Facha no recolecta, permitiendo saber qué tipos de prendas rotan más rápido, cuánto se gana realmente por lote y cuándo conviene hacer un remate.
