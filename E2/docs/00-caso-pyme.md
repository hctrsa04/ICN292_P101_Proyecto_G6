# Caso: Alta Facha (versión de la Entrega 2)

> El caso completo y la evidencia original están en `E1/docs/00-caso-pyme.md` y `E1/evidencia-pyme/`. Este documento resume el caso con las precisiones de las respuestas de la dueña.

## La PYME

Alta Facha es un emprendimiento unipersonal de venta de vestuario femenino por Instagram, en Las Condes. Su dueña es Belén Rojas. Compra ropa por fardo a mayoristas, la plancha, la fotografía, la publica y la vende por mensaje directo. Entrega en persona a las clientas cercanas y, en los demás casos, por un distribuidor.

## El problema

Según las respuestas de Belén al cuestionario del equipo:

- El catálogo publicado en Instagram funciona como su registro activo de stock; el Excel es solo un respaldo.
- Organizar el inventario, los costos por unidad y los registros asociados le toma aproximadamente un día.
- No existe un registro estructurado del costo de cada lote, del margen de cada venta ni de la antigüedad de cada prenda.
- Las prendas sin vender se identifican «al ojo» al final de la temporada.
- Su meta es duplicar lo que recupera de cada lote que compra.

## La solución (Entrega 2)

Un SIG local con base de datos SQLite en 3FN, una aplicación web (Streamlit) para registrar lotes y ventas, y una alerta diaria de remate según la antigüedad del stock. Los indicadores K1 a K5 del tablero responden las preguntas de Belén: cuánto stock tiene, cuánto vende y gana, cuánto recupera de cada lote y qué prendas debería rematar.

Los datos del repositorio son de prueba y ficticios; no son resultados reales de Alta Facha.
