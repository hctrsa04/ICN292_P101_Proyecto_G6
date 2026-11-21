# Entrega 2 (E2) — SIG Alta Facha

**ICN292 · Sistemas de Información para la Gestión · Grupo 6 · Paralelo 101 · UTFSM**

[Volver al README principal](../README.md) · [Consultar la Entrega 1](../E1/README.md)

> **Datos de prueba ficticios.** La base se crea con datos inventados (`app/sql/datos_prueba.sql`); no son resultados reales de Alta Facha. No hay datos personales reales en el repositorio (Ley 21.719).

## 1. Objetivo y alcance

La Entrega 2 desarrolla el prototipo del **Sistema de Información para la Gestión (SIG) de Alta Facha**, microempresa de ropa femenina de segunda mano que vende por Instagram, a partir de los requerimientos, BPMN y arquitectura de la E1.

La aplicación está pensada para **Belén**, la dueña, y se usa desde el celular o el computador: registra lotes, prendas y ventas, confirma entregas, calcula márgenes, genera alertas de remate, prepara fichas para Instagram y muestra un tablero de KPI.

Se ejecuta **localmente**. Instagram, WhatsApp, los cobros y los despachos siguen fuera del SIG: Belén registra en el sistema lo ocurrido por esos canales.

## 2. Arquitectura de la solución

```text
Belén (navegador en computador o teléfono)
                 │
                 ▼
Aplicación web — Streamlit (interfaz)
                 │
                 ▼
Lógica de negocio — Python (funciones_bd.py, kpis.py)
                 │
         instrucciones SQL
                 ▼
Base de datos relacional — SQLite (modelo en 3FN)
         │                   │
         ▼                   ▼
 Consultas / KPI       Automatización
 (SQL + Streamlit)     (script Python)
                             │
                             ▼
                      Alertas de remate
```

**Flujo básico:** la usuaria registra una operación en la interfaz; Python valida la información y la guarda en SQLite en una sola transacción. Las consultas alimentan el tablero de KPI y la automatización revisa a diario las prendas que superan el umbral de días sin venta y registra alertas.

## 3. Estructura de carpetas

```text
E2/
├── README.md                  este archivo
├── app/                       aplicación completa (todo lo necesario para usarla)
│   ├── requirements.txt       dependencias con versiones fijas
│   ├── crear_bd.py            crea data/altafacha.db (schema.sql + datos_prueba.sql)
│   ├── funciones_bd.py        capa de datos: todas las escrituras a la base pasan por aquí
│   ├── kpis.py                consultas de KPI (K1 a K5), solo lectura
│   ├── alerta_remate.py       automatización de alertas de remate
│   ├── ejecutar_alerta.bat    lanza la alerta (Programador de tareas de Windows)
│   ├── probar_consultas.py    ejecuta sql/consultas.sql
│   ├── medir_tiempos.py       mide tiempos de respuesta (RNF-04)
│   ├── sql/                   schema.sql, datos_prueba.sql, consultas.sql, kpi_consultas_propuestas.sql
│   ├── data/                  aquí se crea la base .db (no se sube a git)
│   ├── app/                   interfaz Streamlit: main.py (acceso y menú), formato.py, paginas/
│   ├── tests/                 pruebas unittest
│   └── .streamlit/            secrets.toml.example (la clave real, secrets.toml, no se sube)
├── db/                        scripts SQL y de alerta originales (los del informe, secciones 3 a 5)
├── docs/                      documentación en .md (ver sección 9)
├── assets/                    diagramas y capturas
├── informe/                   informe final (PDF y versión editable)
└── presentacion/              presentación de la defensa
```

`db/` conserva los scripts con que se verificó el informe (`python3 db/crear_bd.py`, `db/probar_consultas.py`, `db/alerta_remate.py`). **Para usar la aplicación no se necesita `db/`**: `app/` trae su propia copia de la base y de los scripts, que además usan la hora local de Chile.

## 4. Requisitos técnicos

- **Python 3.12 o superior** (probado con 3.12 y 3.13).
- **SQLite**, incluido en Python (módulo estándar `sqlite3`).
- **Streamlit 1.67.0** y **pandas 3.1.1** (versiones fijas en `app/requirements.txt`).
- **Git**, para clonar el repositorio.
- Las pruebas usan `unittest` (biblioteca estándar): no hay dependencias de prueba.

## 5. Puesta en marcha (computador limpio)

Los bloques *Windows* son para `cmd` o PowerShell; los demás, para macOS o Linux.

### 5.1 Clonar el repositorio

```bash
git clone https://github.com/hctrsa04/ICN292_P101_Proyecto_G6
cd ICN292_P101_Proyecto_G6/E2/app
```

**Desde aquí, todos los comandos se ejecutan en la carpeta `E2/app`.** Comprueba Python con `python3 --version` (Windows: `py --version`).

### 5.2 Crear el entorno e instalar las dependencias (versiones fijas)

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bat
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Los pasos siguientes suponen el entorno activo.

### 5.3 Crear la base de datos con datos de prueba

```bash
python crear_bd.py
```

Crea `data/altafacha.db` desde `sql/schema.sql` (modelo en 3FN) y `sql/datos_prueba.sql`. **Borra la base anterior y la vuelve a crear**: úsalo solo con datos de prueba.

### 5.4 Crear la clave de acceso

La app pide una clave (RNF-03). No está en el repositorio: cada persona crea la suya.

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml          # macOS / Linux
copy .streamlit\secrets.toml.example .streamlit\secrets.toml        # Windows
```

Abre `.streamlit/secrets.toml` y cambia el texto entre comillas (mantén las comillas): `clave_acceso = "escribe-aqui-tu-clave"`. El archivo está en `.gitignore`.

### 5.5 Levantar la app y ver los KPI

```bash
streamlit run app/main.py
```

Abre <http://localhost:8501>, entra con tu clave y ve al menú **Tablero**. Con la base recién creada (umbral de 30 días) debe mostrar:

| KPI | Valor esperado |
|---|---|
| K1 Inventario por estado | Disponible 13, En remate 1, Vendida 4, Entregada 8 |
| K2 Ventas y margen | Ventas $183.000, margen $145.000 (12 prendas vendidas) |
| K3 Margen bruto | 79,2 %, margen medio por prenda $12.083 |
| K4 Veces la inversión por lote | 2,83 / 2,43 / 1,25 (meta ≥ 2,0: la alcanzan 2 de 3 lotes) |
| K5 Stock sobre el umbral | 53,8 % (7 de 13 prendas disponibles) |

El desplegable "Cómo se calculan estos indicadores" (al final del tablero) muestra la fórmula, la fuente, la meta y el responsable de cada KPI. Detalle en [`docs/05-kpi-dashboard.md`](docs/05-kpi-dashboard.md); código en `app/kpis.py`. Para detener la app: `Ctrl+C`.

### 5.6 Consultas, alerta y pruebas

```bash
python probar_consultas.py                    # ejecuta sql/consultas.sql y muestra los resultados
python alerta_remate.py                       # genera alertas de remate
python -m unittest discover -s tests -v       # pruebas (deben terminar en OK)
python medir_tiempos.py                       # tiempos de respuesta (RNF-04, menos de 3 s)
```

Con la base recién creada, `alerta_remate.py` crea **7 alertas** la primera vez y ninguna la segunda. La misma revisión está en la app (**Alertas → Revisar ahora**). Las pruebas y la medición usan bases temporales: no tocan `data/altafacha.db` ni necesitan `secrets.toml`.

## 6. Cómo usar la aplicación

| Pantalla | Para qué sirve | Requisitos |
|---|---|---|
| Inventario | Resumen por estado, stock por producto (tipo + talla) y detalle de cada prenda | RF-09 |
| Registrar lote | Lote con proveedor, fecha y costo total, y sus prendas con costo y precio por unidad | RF-01, RF-02 |
| Registrar venta | Clienta existente o nueva, productos (carrito), entrega propia o por distribuidor | RF-03, RF-04, RF-05 |
| Entregas | Pedidos pendientes y "Marcar entregado" | RF-08 |
| Alertas | Umbral de días sin venta, "Revisar ahora" y poner prendas en remate con un margen | RF-07, RF-10 |
| Publicar | Ficha de texto para Instagram, lista para copiar | RF-06 |
| Tablero | KPI K1 a K5 | Tablero KPI |

**Recorrido de demostración:** (1) entrar con la clave; (2) **Inventario**: 14 prendas en stock; (3) **Registrar venta** de una prenda disponible y **Entregas** → "Marcar entregado"; (4) **Tablero**: cambian las ventas, el margen y el inventario por estado; (5) **Alertas** → "Revisar ahora": 7 alertas, y definir un margen de remate para una de ellas.

### Alerta diaria automática

`alerta_remate.py` usa solo la biblioteca estándar, así que la tarea programada funciona sin activar el entorno. La base debe existir (`python crear_bd.py`).

- **Windows (Programador de tareas):** Crear tarea básica → Diariamente → Iniciar un programa → `ejecutar_alerta.bat` de la carpeta `E2/app` (en "Iniciar en", la ruta de esa carpeta). Cada ejecución se agrega a `data/registro_alertas.txt`.
- **macOS / Linux (cron):** `crontab -e` y agregar (cambiando la ruta):

  ```cron
  0 9 * * * cd "/ruta/a/E2/app" && python3 alerta_remate.py >> data/registro_alertas.txt 2>&1
  ```

El detalle y las pruebas de la automatización están en [`docs/05-automatizacion.md`](docs/05-automatizacion.md).

## 7. Abrir la app desde el celular

Con el celular y el computador en la misma red Wi-Fi:

1. Levanta la app con `streamlit run app/main.py --server.address 0.0.0.0`.
2. Busca la IP del computador (macOS: `ipconfig getifaddr en0`; Windows: `ipconfig`).
3. En el celular abre `http://<IP-del-computador>:8501` y acepta el aviso de firewall si aparece.

## 8. Limitaciones del prototipo

- **Disponibilidad (RNF-02) no garantizada:** la app corre en `localhost`; si el computador está apagado, no está disponible.
- **Datos ficticios:** no hay datos reales de clientas en el repositorio (Ley 21.719, ver [`docs/07-etica-ley-21719.md`](docs/07-etica-ley-21719.md)).
- Otras limitaciones del desarrollo: [`docs/09-limitaciones.md`](docs/09-limitaciones.md). Reglas confirmadas y decisiones pendientes con Belén: [`docs/08-supuestos.md`](docs/08-supuestos.md).

## 9. Documentación y entregables

| Ubicación | Contenido |
|---|---|
| `docs/00-caso-pyme.md` | Resumen del caso Alta Facha y del problema |
| `docs/02-bpmn.md` | BPMN As-Is y To-Be finales, cambios respecto de la E1 y dónde se implementa cada tarea |
| `docs/01-requerimientos.md` | RF y RNF con su estado y la trazabilidad requisito → código → prueba |
| `docs/04-er-3fn.md` | Modelo entidad-relación en 3FN, normalización y trazabilidad BPMN → entidades |
| `docs/04-sql-consultas.md` | Consultas SQL de negocio, resultados e interpretación |
| `docs/05-automatizacion.md` | Automatización de la alerta de remate, con pruebas y capturas |
| `docs/05-kpi-dashboard.md` | KPI: fórmula, fuente en el modelo, meta y responsable |
| `docs/07-etica-ley-21719.md` | Riesgos y medidas de protección de datos (Ley 21.719) |
| `docs/08-supuestos.md`, `docs/09-limitaciones.md` | Reglas de negocio confirmadas, decisiones pendientes y limitaciones |
| `docs/CHANGELOG.md` | Cambios relevantes entre la E1 y la E2 |
| `assets/` | Diagramas BPMN, ER y capturas de las pruebas |
| `informe/` | Informe E2 en PDF y versión editable (Word o LaTeX) |
| `presentacion/` | Presentación de la defensa |
| `../E1/` | Documentación de la Entrega 1 (caso, requerimientos, BPMN, arquitectura) |

## 10. Problemas comunes

| Mensaje o síntoma | Solución |
|---|---|
| "No se encontró la base de datos" | Ejecuta `python crear_bd.py` |
| "Falta configurar la clave de acceso" | Haz el paso 5.4 y reinicia la app |
| `ModuleNotFoundError: streamlit` | Activa el entorno (paso 5.2) antes de ejecutar |
| "Port 8501 is already in use" | Cierra la otra app con `Ctrl+C` o usa `--server.port 8502` |
| "database is locked" | Cierra otros programas que tengan abierta `data/altafacha.db` |

## 11. Participantes

**Grupo 6 — P101:** Diego Victoriano, Matías Castro, Ricardo García, Iván González y Héctor Sánchez.

Para una visión general del caso y de ambas entregas, consulta el [README principal](../README.md).
