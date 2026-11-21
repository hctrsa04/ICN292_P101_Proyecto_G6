# KPI y tablero

> Las rutas de código, consultas y pruebas de este documento son relativas a `E2/app/`.

**Estado final (21-nov):** K1 a K5 están **implementados** en `kpis.py` (una función de solo lectura por KPI, con fórmula y fuente en su docstring) y se muestran en la pantalla **Tablero** (`app/paginas/tablero.py`). Sus valores se prueban en `tests/test_kpis.py` contra la tabla de valores de este documento. Las metas son fijas: solo K4 tiene meta definida y las demás dicen "por definir con Belén"; no se editan desde la app (limitación L4 en `Limitaciones_en_desarrollo.md`).

**Antecedentes:** los KPI partieron semi definidos. Las consultas base están en `sql/consultas.sql`; las propuestas, en `sql/kpi_consultas_propuestas.sql`. Las **metas** se acuerdan con Belén, salvo una que ya consta en el informe E2: **duplicar lo invertido en cada lote** (K4). No inventar otras metas ni resultados.

**Concordancia con el informe E2 (revisada el 21-nov):** las cifras de la base de prueba coinciden con las del informe (Tabla 1 y consultas 1 a 3 de la sección 5). Cambios hechos en este documento por esa revisión: meta de K4, valores de verificación de K2, K3, K4 y K5, y aviso de datos ficticios.

**Nota del equipo (19-nov):** las consultas SQL actuales se hicieron para apoyar la operación del BPMN to-be y **no** se dan por KPI definitivos. Ricardo cierra la definición final con Belén y se verifica contra el SQL con los valores de este documento.

## Objetivo (OKR)

**Objetivo:** que Belén decida qué comprar, a qué precio vender y cuándo rematar usando datos del negocio y no la memoria.

Resultados clave: cada KPI de la tabla, con su meta, una vez acordada con Belén.

## Tabla de KPI

| Código | KPI | Fórmula | Fuente en el modelo | Consulta | Meta | Responsable | Estado |
|---|---|---|---|---|---|---|---|
| K1 | Inventario por estado | Conteo de prendas por estado | `Prenda.estado` | `consultas.sql` 1c / `inventario_por_estado()` | Por definir con Belén | Belén | Implementado: `k1_inventario_por_estado()` |
| K2 | Ventas y margen bruto mensual | Suma de `precio_final` y `margen` por mes de `fecha_venta` | `DetallePedido`, `Pedido` | `consultas.sql` 2b | Por definir con Belén | Belén | Implementado: `k2_ventas_margen_mensual()` |
| K3 | Margen bruto % | Suma de `margen` / suma de `precio_final` × 100. Complemento: margen medio por prenda = suma de `margen` / prendas vendidas | `DetallePedido` | `kpi_consultas_propuestas.sql` K3 | Por definir con Belén | Belén | Implementado: `k3_margen_bruto()` |
| K4 | Recuperación de la inversión por lote | `veces_inversion` = ventas / `costo_total`. Complementos: resultado neto = ventas − `costo_total`; % vendido | `Lote`, `Prenda`, `DetallePedido` | `consultas.sql` 2c y K4 | **≥ 2,0 veces** (duplicar lo invertido). Origen: Belén, respuesta 2 del cuestionario; informe E2, secciones 1.3 y 5.2 | Belén | Implementado: `k4_recuperacion_por_lote()` |
| K5 | % de stock sobre el umbral | Disponibles con días > umbral / disponibles | `Prenda`, `Lote`, `Configuracion` | `consultas.sql` 3 y K5 | Por definir con Belén | Belén | Implementado: `k5_stock_sobre_umbral()` |

Alcance del tablero de la Entrega 2: **K1 a K5**, todos con respaldo en el informe E2. Se retiraron el 21-nov los KPI K6 a K9 (rotación, tipos más vendidos, clientas frecuentes y pedidos sin entregar) porque no aparecen en el informe y podrían generar discordancia de datos. Si el equipo los quiere más adelante, hay que agregarlos primero al informe.

## Respaldo en el informe E2

| KPI | Dónde aparece en el informe |
|---|---|
| K1 | Tabla 1 (stock) y consultas 1, 1b |
| K2 | Consulta 2b |
| K3 | Tabla 1 (margen 79,2 %) y consulta 2 (margen medio ≈ 12.083) |
| K4 | Tabla 1 y consulta 2c (veces la inversión y meta de duplicar) |
| K5 | Consulta 3 y alerta de remate (umbral 30 y umbral 50) |

## Valores de la base de prueba (para verificar que el tablero muestra lo mismo que el SQL y el informe)

Base recién creada con `python crear_bd.py` y umbral 30.

| KPI | Valor esperado |
|---|---|
| K1 | disponible 13, en remate 1, vendida 4, entregada 8 (stock = 14; 26 prendas en total). Complemento, stock por tipo (consulta 1b): blusa 5, falda 3, abrigo 2, chaqueta 2, vestido 2 |
| K2 | 12 prendas vendidas en 7 pedidos, ventas 183.000 y margen 145.000. **No fijar el reparto por mes en los tests:** las fechas de prueba son relativas y ese reparto cambia según el día en que se crea la base |
| K3 | 79,2 %; margen medio por prenda 12.083 |
| K4 | `veces_inversion`: lote 1 = 2,83, lote 2 = 2,43, lote 3 = 1,25. Ventas: 85.000 / 68.000 / 30.000. Resultado neto: 55.000 / 40.000 / 6.000. % vendido: 60 % / 50 % / 25 %. Los lotes 1 y 2 superan la meta de 2,0; el lote 3 aún no (recibido hace 10 días, 2 de 8 prendas vendidas) |
| K5 | Umbral 30: 7 de 13 (53,8 %). Umbral 50: 3 de 13 (23,1 %) |

## Puntos abiertos (se resuelven con Belén; hasta entonces mantener el comportamiento actual)

| # | Tema | Qué hace hoy el código | Pregunta |
|---|---|---|---|
| 2 | "Días sin venta" | Cuenta desde `Lote.fecha_recepcion` | ¿Desde la llegada del lote o desde que publica la prenda? |
| 3 | Margen | Margen bruto por prenda = `precio_final` − costo individual de la prenda (`Prenda.costo`). **Confirmado:** cada prenda tiene su costo y no se reparte el del lote (R1 en `08-supuestos.md`). No resta despacho ni otros costos | ¿Quién paga el despacho? ¿Cómo se valida la suma de costos contra `Lote.costo_total` (P1)? |
| 5 | Definición de "stock" | **Resuelto (R2):** stock comercializable = `disponible` + `en_remate` (consultas 1, 1b, 1c). La consulta 3 y la alerta evalúan solo `disponible` | — |
| 6 | Devoluciones | No existen (una prenda se vende una sola vez) | ¿Ocurren? ¿Qué pasa con la prenda? |
| 7 | Borde del umbral | Alerta con `días > umbral` en días fraccionarios: una prenda de 30 días con umbral 30 se alerta el mismo día 30 | ¿Alertar el día 30 o el 31? |

## Reglas para el tablero

- Cada KPI muestra su fórmula, su fuente, su meta y su responsable, para cumplir el enunciado. En la app están en el desplegable "ℹ️ Cómo se calculan estos indicadores", al final del tablero. Solo K4 tiene meta hoy (≥ 2,0 veces); los demás dicen "por definir con Belén".
- El tablero muestra un aviso visible: "Datos de prueba ficticios, no son resultados reales de Alta Facha" (coherente con el informe E2, sección 7.2).
- Todos los números del tablero deben salir de consultas SQL sobre la base. Nada calculado "a mano" ni inventado.
- Las consultas de los KPI viven en un solo módulo (`kpis.py`), de solo lectura, para poder cambiarlas fácil cuando Belén responda.
