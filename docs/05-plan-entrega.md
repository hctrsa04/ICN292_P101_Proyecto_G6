[Plan_entrega_2_y_riesgos.md](https://github.com/user-attachments/files/32128203/Plan_entrega_2_y_riesgos.md)

# G. Plan de entrega 2 y riesgos a considerar

Para la entrega 2 el equipo comenzara a trabajar durante la segunda/tercera semana de Octubre (suponiendo que ya se tenga el feedback de la primera entrega). Durante la semana del 15 al 19 de Octubre se avanzará en la normalización del modelo de datos a 3FN, dando forma al ER final.

Entre 20 y 22 de Octubre se completará el diccionario de datos con todo lo necesario y relacionado al negocio. Una vez se tenga el ER ya normalizado y el diccionario definido comenzamos, entre 23 y 25 de Octubre, a documentar la trazabilidad entre ambas entregas, señalando que se cambió y que se mantuvo en el BPMN y en el ER.

Entre el 26 de Octubre y el 1 de Noviembre se elaborará el script SQL. Entre 2 y 6 de Noviembre se diseñarán y ejecutarán las consultas de negocio alineadas al problema de la PYME, junto con una interpretación de sus resultados.

Entre el 7 y 13 de Noviembre se implementará el tablero KPI, formalizando los indicadores bajo el esquema KPI/OKR. Entre el 14 y el 18 de Noviembre, se diseñará y documentará el flujo de la automatización en n8n (u homologo), conectado al proceso to-be.

En la semana del 19 al 21 de Noviembre se consolidará el repositorio GitHub, cerciorándonos que contenga con toda la documentación en el formato solicitado. Y finalmente en paralelo a la consolidación del repositorio, en los últimos días hasta la fecha límite de envío se redactará el informe final junto con la presentación de contexto.

Durante todo este tiempo, desde 15 de Octubre hasta el 23 de Noviembre se llevarán a cabo reuniones de forma online con la PYME, solo de ser necesarias. Este cronograma puede estar sujeto a cambios.

Además, el responsable de cada tarea/ hito se mantendrá en espera. La asignación de responsables se hará la semana anterior al inicio del cronograma.

image

## Riesgos Ley 21.719

### Riesgo 1 - Uso de datos

Al construir base de datos SQL y cargarla con información del caso, existe riesgo de incorporar datos reales clientes o transacciones sin que exista un consentimiento explicito. La ley exige que toda recolección de datos personales cuente con una base de licitud clara, por lo que sería necesario obtener consentimiento antes de poder dar uso a los datos.

### Riesgo 2 - Exponer información confidencial en el repositorio

Como el repositorio deber ser público y clonable por el docente, cualquier dato que se suba al repositorio queda sin una forma de controlar el acceso.

### Riesgo 3 – Automatización n8n conectada a datos sensibles

Una automatización que mueve datos entre sistemas sin registro de la información que procesa, cuando y por qué, es lo que la ley busca evitar. Por lo que se debe documentar el flujo del n8n señalando que datos puede tocar y los controles de acceso disponibles.

### Riesgo 4 – Ausencia de mecanismo de derechos

Los titulares de los datos ocupados tienen derecho a saber qué información se tiene sobre ellos y pueden solicitar la eliminación de estos datos. El sistema propuesto no contempla ninguna acción para ejercer estos derechos.

### Riesgo 5 – Retención de datos

No se ha definido que ocurre con los datos utilizados una vez acabado el proyecto. La ley contempla que la personas tienen derecho a solicitar la supresión de su información y exige a las organizaciones que no conserven más información de la necesaria.
