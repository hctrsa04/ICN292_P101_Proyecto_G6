Gestión de Riesgos y protección de datos

El SIG. Para la pyme Alta Facha tiene contemplado el registro de inventario, ventas y datos de los clientes. Es por ello por lo que, además de los riesgos asociados al funcionamiento del sistema, es necesario considerar el tratamiento de la información personal del consumidor.

Teniendo en cuenta la Ley 21.719, que entra en vigor el 1 de Diciembre, se analizaron los riesgos antes identificados en E1 y se definieron medidas para reducirlos.

**Riesgo 1. Uso inadecuado de datos personales**

El sistema contempla almacenar nombres, datos de contacto e historial de compras de los clientes. Por ello existe el riesgo para los clientes que esta información se use sin una base legal o de registrar datos personales innecesarios para el negocio.

Como medida de mitigación, durante el desarrollo y pruebas del prototipo se utilizaron datos anónimos. Además, se limitará el registro de datos solo a la información necesaria para identificar a cada cliente y sus respectivas compras. Antes de incorporar los datos se deberá definir la finalidad del tratamiento e informar a los clientes sobre el uso de su información.

**Riesgo 2. Exposición de información confidencial en GitHub.**

El repositorio GitHub será público, esto genera el riesgo de publicar accidentalmente la información personal de los clientes. Para reducir este riesgo, los archivos del repositorio deberán contener únicamente la información necesaria.

Antes de publicar nuevas versiones, se revisará que los archivos incorporados no contengan información personal. La BBD utilizada para la demostración deberá contener solamente registros ficticios, permitiendo reproducir la solución sin comprometer información de Alta Facha

**Riesgo 3. Automatización conectada a información sensible**

La solución contempla una automatización independiente en Streamlit, cuyo objetivo es consultar periódicamente la base SQLite para identificar aquellas prendas disponibles que superen cierto umbral de días sin venderse.

Una configuración incorrecta de esta podría provocar accesos a información innecesaria, alertas equivocadas o modificaciones accidentales en los registros.

Para mitigar este riesgo, la automatización solo consultara los campos necesarios para identificar las prendas y determinar la antigüedad. Se debe limitar sus permisos de acceso, evitando así modificaciones en los datos cuando no sea necesario.

**Riesgo 4. Ausencia de mecanismos para ejercer derechos sobre los datos personales**

Al almacenar información de las clientas en SQLite, existe el riesgo de no contar con un procedimiento para responder a solicitudes de acceso, rectificación o eliminación de sus datos personales.

Como medida de mitigación, se deberá dejar documentada esta limitación del prototipo y establecer que, antes de utilizar el sistema con información real de las clientas, Alta Facha deberá contar con un procedimiento para recibir y gestionar dichas solicitudes. Este procedimiento deberá considerar la identificación de los datos asociados a cada clienta y las condiciones bajo las cuales corresponda modificarlos o eliminarlos, de acuerdo con la normativa aplicable.

**Riesgo 5. Retención o perdida de información**

El almacenar datos sin criterios definidos puede provocar que se mantenga información personal durante más tiempo del necesario. Además, al usar SQLite existe el riesgo de perder registros necesarios debido a diversas fallas.

Para reducir esto riesgos, se definen criterios de conservación según el tipo de información y su finalidad. Los registros que ya no sean necesarios deben eliminarse al finalizar su utilización.

También, se recomienda mantener respaldos periódicos de la base SQLite en una ubicación protegida y comprobar que se puedan recuperar correctamente.

**Riesgo 6. Inconsistencias entre ventas y el inventario**

Uno de los principales problemas de Alta Facha es la actualización manual del inventario luego de cada venta. El SIG busca automatizar este proceso, aun con ello existe el riesgo de que se registren transacciones sin actualizar correctamente el estado de la prenda.

Para prevenirlo, se propone utilizar transacciones SQL que permitan ejecutar el registro de la venta y la actualización del inventario como una única operación. De esta forma, los cambios deberán confirmarse conjuntamente, en caso de producirse un error se deberá revertir para evitar registros incompletos.

También se deberán validar las condiciones de disponibilidad antes de confirmar una venta, impidiendo registrar nuevamente una prenda que ya se encuentre vendida o entregada.
