# Arquitectura lógica y stack tentativo

## Enfoque de la solución

A partir de los requerimientos definidos y del proceso To-Be, se propone desarrollar el SIG de Alta Facha como una aplicación web de uso interno y de baja sofisticación, orientada a centralizar el registro de inventario, ventas y clientes, automatizando aquellas tareas que actualmente presentan un mayor riesgo de error, pero que también sea adoptable al uso de la usuaria.

Considerando que la operación cotidiana de Alta Facha se realiza principalmente desde el teléfono móvil, se privilegiará una interfaz simple, con pocas acciones de ingreso manual. De esta manera, la interacción de la usuaria se concentrará principalmente en registrar lotes, ventas, confirmar entregas y consultar información, mientras que operaciones como la actualización del estado del inventario, el cálculo de márgenes y la generación de indicadores serán realizadas por el sistema de manera automática.

La propuesta no busca reemplazar los actuales canales comerciales de Alta Facha. Instagram y WhatsApp continuarán siendo utilizados para la publicación de prendas y la comunicación con las clientas, mientras que la gestión de pagos y despachos permanecerá fuera del alcance del SIG. En consecuencia, la aplicación actuará como una herramienta interna de control y apoyo a la toma de decisiones.

Para la Entrega 2 se implementará un prototipo funcional y reproducible en `localhost`. Por lo tanto, el alcance actual corresponde a la validación de la solución propuesta y de su integración entre proceso, datos y analítica, quedando un eventual despliegue productivo para uso remoto de la PYME fuera del alcance de esta etapa.

## Arquitectura lógica

La arquitectura propuesta se organiza en torno a una aplicación web que concentra la interacción de la usuaria y se conecta con una base de datos relacional. A partir de los datos almacenados, el sistema permitirá ejecutar consultas de negocio, calcular y visualizar indicadores, además de incorporar una automatización asociada al proceso To-Be. El diagrama de arquitectura lógica se encuentra en la carpeta `assets/` del repositorio.

La **aplicación web** será el principal punto de interacción de Belén con el SIG. Desde ella será posible registrar información asociada a lotes, prendas, ventas y clientes, actualizar el estado de las entregas, consultar el inventario y acceder a los principales indicadores del negocio.

La **lógica de aplicación** ejecutará las reglas definidas en los requerimientos funcionales, entre ellas la generación de fichas de prendas, la validación y actualización del stock, el cambio de estado de las prendas, el cálculo de márgenes y el registro o actualización de la información de clientes.

La **capa de persistencia** estará compuesta por una base de datos relacional, cuyo modelo definitivo será obtenido a partir de la normalización a tercera forma normal (3FN) durante la Entrega 2 (E2). Esta capa permitirá centralizar la información que actualmente se mantiene de manera manual y mantener trazabilidad sobre inventario, clientes y transacciones.

Sobre los datos almacenados se incorporará un componente de **analítica y KPI**, encargado de ejecutar consultas de negocio y presentar información relevante para la gestión, como el estado del inventario, ventas realizadas, márgenes y antigüedad de las prendas. De forma complementaria, se contempla un componente de **automatización**, asociado principalmente a la revisión periódica de prendas que superen el umbral definido de días sin venta y a la generación de alertas de remate.

## Stack tecnológico tentativo

Considerando el tamaño de la PYME, la existencia de una única usuaria operativa y la necesidad de implementar una solución reproducible en `localhost`, se propone un stack tecnológico sencillo. Su propósito es satisfacer los requerimientos del SIG sin incorporar una complejidad técnica innecesaria.

| Componente | Tecnología | Aplicación en el proyecto |
|---|---|---|
| Aplicación web | Python + Streamlit | Desarrollo de formularios, vistas de consulta y tablero de indicadores en una misma aplicación. |
| Persistencia | SQLite | Almacenamiento local y relacional de la información del negocio. |
| Consultas de negocio | SQL | Obtención y procesamiento de información para análisis e indicadores. |
| Analítica y KPI | Streamlit + SQL | Visualización de métricas asociadas a inventario, ventas, márgenes y rotación. |
| Automatización | n8n o herramienta homóloga | Ejecución de procesos periódicos vinculados al BPMN To-Be, especialmente la detección de prendas que superen el umbral de días sin venta. |
| Control de versiones y documentación | GitHub | Almacenamiento del código, scripts SQL, documentación y trazabilidad del proyecto. |
| Ambiente de ejecución | Localhost | Ejecución reproducible de la solución durante la Entrega 2. |

La elección tentativa de Python, Streamlit y SQLite permite integrar la captura, consulta y visualización de información en una solución de baja complejidad técnica. SQLite resulta suficiente para el volumen y nivel de concurrencia esperado en el caso de Alta Facha y, al mismo tiempo, permite materializar el modelo relacional mediante SQL.

La aplicación será documentada en el repositorio GitHub junto con las dependencias, scripts de creación y carga de la base de datos e instrucciones necesarias para que un tercero pueda reproducir la solución en `localhost`. La arquitectura y el stack podrán ser ajustados durante la Entrega 2 en función de la normalización del modelo de datos y de los resultados obtenidos durante la implementación.
