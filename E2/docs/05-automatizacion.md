# 05. Automatización: alerta de remate

## 5.1 Qué se automatiza

Se automatizó la parte de remate del BPMN To-Be ([02-bpmn.md](02-bpmn.md)):

> Revisión periódica (temporizador) → Evaluar días sin venta por prenda → ¿Supera el umbral? (XOR) → Generar alerta de remate

Antes, Belén revisaba a ojo, al final de cada temporada, qué prendas no se habían vendido. Ahora el sistema revisa todos los días qué prendas llevan más días sin venderse que el umbral que ella definió, y deja una alerta para que decida el remate.

## 5.2 Herramienta usada

El enunciado permite usar n8n o una herramienta homóloga. Se usó:

- **`alerta_remate.py`**: script de Python que hace la revisión y crea las alertas en la base `data/altafacha.db`.
- **`ejecutar_alerta.bat`**: ejecuta el script y guarda la salida en `data/registro_alertas.txt`.
- **Programador de tareas de Windows**: ejecuta el `.bat` una vez al día. Cumple el papel del evento temporizador del BPMN.

Se eligió esta opción porque el script trabaja directo sobre SQLite, se puede probar y repetir sin instalar nada más que Python, y no depende de conectar n8n a la base. Si se quisiera usar n8n, bastaría un flujo con un nodo *Schedule Trigger* diario y un nodo *Execute Command* que ejecute `python alerta_remate.py`; la lógica sería la misma.

## 5.3 Evento, datos, lógica y resultado

**Evento que la activa:** la tarea programada **"Alerta de remate - Alta Facha"**, que se ejecuta diariamente.

**Datos que usa:**

| Tabla | Para qué |
|-|-|
| `Configuracion` | Lee `umbral_dias`, el umbral de días sin venta que define Belén |
| `Lote` | Lee `fecha_recepcion`, desde donde se cuentan los días sin venta |
| `Prenda` | Lee el `estado`; solo se revisan las prendas `disponible` |
| `AlertaRemate` | Revisa si la prenda ya tiene una alerta pendiente y guarda las nuevas |

**Lógica:**

1. Lee el umbral desde `Configuracion`.
2. Busca las prendas en estado `disponible` cuyos días desde la recepción de su lote superan el umbral.
3. Por cada prenda encontrada, inserta una fila en `AlertaRemate` con `estado_alerta = 'pendiente'` y los días sin venta, salvo que esa prenda ya tenga una alerta pendiente. Así no se duplican alertas si el script corre varios días seguidos.
4. Si no encuentra prendas, termina sin crear alertas (es la salida "Sin prendas para remate" del XOR).

**Resultado:** las alertas quedan en la tabla `AlertaRemate` y la app las muestra a Belén. Cuando ella atiende una alerta, ingresa el margen de remate y el sistema:

- calcula `precio_remate = costo * (1 + margen)`;
- cambia la prenda a `en_remate`;
- marca la alerta como `atendida`.

Esto corresponde a las tareas "Definir margen de remate" y "Calcular precio de remate" del To-Be, y se hace con la función `atender_alerta(id_alerta, margen)` de `funciones_bd.py`.

## 5.4 Cómo ejecutarla

Desde la carpeta donde están los scripts, con la base ya creada (`python crear_bd.py`):

```
python alerta_remate.py
```

Para cambiar el umbral (lo hace Belén desde la app):

```sql
UPDATE Configuracion SET umbral_dias = 50 WHERE id_config = 1;
```

## 5.5 Cómo se programó

En el Programador de tareas de Windows:

1. **Crear tarea básica**, con el nombre "Alerta de remate - Alta Facha".
2. **Desencadenador:** diariamente, a las 0:50.
3. **Acción:** iniciar un programa → `ejecutar_alerta.bat`, con "Iniciar en" igual a la carpeta de los scripts.
4. Cada ejecución queda registrada en `data/registro_alertas.txt`.

## 5.6 Pruebas

Las pruebas se hicieron con los datos de `datos_prueba.sql`, con un umbral inicial de 30 días.

| N.º | Prueba | Resultado esperado | Resultado obtenido | Evidencia |
|-|-|-|-|-|
| 1 | Primera ejecución del script | Alertas para las prendas disponibles sobre el umbral | 7 alertas creadas | [captura](../assets/automatizacion/01_alerta_primera_ejecucion.png) |
| 2 | Segunda ejecución, sin cambios en la base | Ninguna alerta nueva (no se duplican) | Sin prendas para remate | [captura](../assets/automatizacion/02_alerta_segunda_ejecucion.png) |
| 3 | Revisar la tabla `AlertaRemate` | Alertas nuevas como pendientes | 1 atendida y 7 pendientes | [captura](../assets/automatizacion/03_tabla_alertaremate.png) |
| 4 | Cambiar el umbral a 50 días | Umbral actualizado en `Configuracion` | `UPDATE` ejecutado | [captura](../assets/automatizacion/04_umbral_update_50.png) |
| 5 | Ejecutar con umbral 50 | Menos prendas sobre el umbral | 3 alertas | [captura](../assets/automatizacion/05_alerta_umbral_50.png) |
| 6 | Registro de ejecuciones | Cada ejecución queda escrita en el registro | Dos revisiones en `registro_alertas.txt` | [captura](../assets/automatizacion/06_registro_alertas.png) |
| 7 | Desencadenador de la tarea | Tarea diaria configurada | Diariamente a las 0:50 | [captura](../assets/automatizacion/07_tarea_desencadenador.png) |
| 8 | Ejecución programada | La tarea corre sin error | Resultado 0x0 (completada correctamente) | [captura](../assets/automatizacion/08_tarea_resultado_0x0.png) |

## 5.7 Limitaciones

- La tarea programada solo corre si el computador está encendido a esa hora. En un uso real convendría un equipo siempre encendido o un servicio en la nube.
- La alerta solo avisa; la decisión del remate y del margen sigue siendo de Belén, como se definió en el To-Be.
- Los días sin venta se cuentan desde la recepción del lote y no desde la publicación, porque así se definió en el modelo de datos. Si una prenda se publica tarde, puede aparecer en la alerta antes de lo que correspondería.
