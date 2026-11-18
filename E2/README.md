# Entrega 2 (E2) — SIG Alta Facha

**ICN292 · Sistemas de Información para la Gestión · Grupo 6 · Paralelo 101 · UTFSM**

[Volver al README principal](../README.md) · [Consultar la Entrega 1](../E1/README.md)

## 1. Objetivo y alcance

La Entrega 2 desarrolla el prototipo del **Sistema de Información para la Gestión (SIG) de Alta Facha** a partir de los requerimientos, modelos BPMN y arquitectura diseñados en E1.

La aplicación está orientada principalmente a **Belén**, dueña del emprendimiento, para gestionar de forma simple el registro de lotes, prendas, clientes y ventas, consultar existencias, confirmar entregas, calcular márgenes y visualizar información comercial.

El prototipo se ejecuta **localmente**. Instagram, WhatsApp, los cobros y los servicios de despacho continúan fuera del SIG: Belén registra en el sistema la información de operaciones realizadas por esos canales.

## 2. Arquitectura de la solución

```text
Belén (navegador en computador o teléfono)
                 │
                 ▼
Aplicación web — Streamlit (interfaz)
                 │
                 ▼
Lógica de negocio — Python
                 │
         instrucciones SQL
                 ▼
Base de datos relacional — SQLite
         │                   │
         ▼                   ▼
 Consultas / KPI       Automatización
 (SQL + Streamlit)     (script Python)
                             │
                             ▼
                      Alertas de remate
```

**Flujo básico:** la usuaria registra una operación en la interfaz; Python valida la información y lee o modifica SQLite. Las consultas alimentan el tablero KPI; la automatización revisa periódicamente prendas que superan el umbral configurado y registra alertas.

## 3. Estructura de carpetas

La siguiente es la **estructura objetivo**. Las piezas de la interfaz y la documentación pendiente se incorporarán durante la integración final.

```text
E2/
├── README.md
├── requirements.txt              # Por completar al fijar dependencias de la app
├── app/
│   └── app.py                    # Aplicación Streamlit: pendiente de integrar
├── db/
│   ├── crear_bd.py               # Inicializa SQLite con datos de prueba
│   ├── probar_consultas.py       # Ejecuta las consultas SQL
│   ├── alerta_remate.py          # Detecta prendas y genera alertas
│   ├── funciones_bd.py           # Funciones de lectura y escritura para la app
│   ├── sql/
│   │   ├── schema.sql            # Tablas y restricciones
│   │   ├── datos_prueba.sql      # Datos de demostración
│   │   └── consultas.sql         # Consultas de negocio
│   └── data/                    # Base local generada (no versionarla)
├── docs/                        # ER 3FN, BPMN, KPI, ética y trazabilidad
├── assets/                      # Diagramas e imágenes
├── informe/                     # Informe final (PDF y fuente editable)
└── presentacion/                # Presentación para la defensa
```

> **Importante al mover los ZIP:** conservar los scripts `crear_bd.py`, `probar_consultas.py`, `alerta_remate.py` y `funciones_bd.py` junto a las subcarpetas `sql/` y `data/` dentro de `db/`. Sus rutas actuales están construidas con la carpeta del script. Si se distribuyen en carpetas distintas, es necesario actualizar las rutas.

## 4. Requisitos técnicos

- **Python 3** instalado en el computador. Registrar aquí la versión concreta que use el equipo antes de entregar.
- **SQLite**, disponible mediante el módulo estándar `sqlite3` de Python.
- **Streamlit**, para la interfaz de usuario, y otras dependencias que finalmente use la aplicación.
- **Git**, para clonar el repositorio y consultar el historial.

**Pendiente para la versión final:** publicar `requirements.txt` con versiones fijadas, indicar versiones probadas de Python/Streamlit y confirmar el sistema operativo de la prueba de instalación limpia.

## 5. Preparación de la base de datos (scripts ya recibidos)

Una vez ubicados los archivos del ZIP `AltaFacha_SIG` según la estructura del apartado 3, abre una terminal en la raíz **E2/** y ejecuta:

```bash
python3 db/crear_bd.py
python3 db/probar_consultas.py
python3 db/alerta_remate.py
```

En **Windows**, si `python3` no está disponible, normalmente se utiliza `python` o `py`.

| Comando | Resultado esperado |
|---|---|
| `crear_bd.py` | Crea `db/data/altafacha.db`, aplica el esquema y carga datos sintéticos. |
| `probar_consultas.py` | Ejecuta las consultas definidas en `db/sql/consultas.sql` y muestra resultados en la terminal. |
| `alerta_remate.py` | Revisa prendas disponibles que superan el umbral y registra alertas pendientes. |

**Advertencia:** `crear_bd.py` **elimina y recrea** la base `altafacha.db` si ya existe. Úsalo solamente para reiniciar los **datos de prueba**; no lo ejecutes sobre registros que deban conservarse.

Las cifras obtenidas son ilustrativas y proceden de `datos_prueba.sql`; no deben interpretarse como resultados reales de la PYME.

## 6. Ejecución de la aplicación web (pendiente de completar)

Cuando se integre la aplicación Streamlit, los pasos previstos desde **E2/** serán:

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
python3 -m pip install -r requirements.txt
python3 -m streamlit run app/app.py
```

En **Windows**, la activación del entorno virtual normalmente se realiza con:

```powershell
.venv\Scripts\Activate.ps1
```

Luego se abrirá la dirección local que indique Streamlit (habitualmente `http://localhost:8501`).

**Estado actual de estas instrucciones:** los comandos de los scripts SQL corresponden a archivos recibidos. El comando de Streamlit es la **ruta prevista** y solo será verificable cuando existan `app/app.py` y `requirements.txt`. Debe probarse la instalación de principio a fin antes de cerrar la entrega.

## 7. Funciones y operaciones principales

Las funciones Python existentes en `db/funciones_bd.py` incluyen:

| Función | Uso |
|---|---|
| `stock_disponible()` | Consulta prendas disponibles y en remate. |
| `obtener_umbral()` / `actualizar_umbral(dias)` | Consulta y modifica el umbral de antigüedad. |
| `alertas_pendientes()` / `atender_alerta(...)` | Consulta y gestiona las alertas de remate. |
| `registrar_venta(...)` | Registra pedidos y actualiza estados y márgenes. |
| `marcar_entregado(id_pedido)` | Registra la entrega de un pedido. |

**Pendiente de integración:** conectar estas funciones a la interfaz y completar las operaciones de registro de lotes, prendas y clientes. Alinear también la captura del precio realmente cobrado y las rutas de importación desde `app/`.

## 8. Consultas, KPI y automatización

Las consultas SQL ya preparadas consideran inventario disponible, ventas, márgenes, análisis por lote y prendas con antigüedad superior al umbral.

La definición final de **cada KPI** debe registrar fórmula, fuente SQL, periodicidad, meta y decisión de negocio; el tablero Streamlit debe mostrar valores calculados desde la base, no cifras escritas manualmente.

El archivo `db/alerta_remate.py` implementa una revisión de prendas disponibles y genera alertas en la tabla `AlertaRemate`. La ejecución del script puede probarse manualmente con el comando indicado antes. La programación automática diaria debe configurarse y documentarse por separado: el ZIP original trae un `.bat` para Windows, pero no una programación equivalente para macOS/Linux.

## 9. Documentación y entregables

| Carpeta | Qué debe contener al cierre |
|---|---|
| `docs/` | Contexto PYME, requerimientos, BPMN final, ER 3FN y diccionario, consultas, KPI/OKR, automatización, Ley 21.719 y trazabilidad E1 → E2. |
| `assets/` | Diagramas e imágenes legibles referenciados desde los documentos. |
| `informe/` | Informe E2 en PDF y versión editable con el mismo contenido. |
| `presentacion/` | Presentación de defensa. |

Se debe incorporar un registro de cambios (`CHANGELOG.md` o equivalente) y los archivos de documentación `.md` necesarios para explicar el trabajo realizado.

## 10. Lista de validación previa a entrega

- [ ] ER final, scripts y modelo BPMN son coherentes entre sí.
- [ ] Un tercero puede clonar el repositorio y crear la base desde cero.
- [ ] `probar_consultas.py` produce resultados sin errores.
- [ ] La aplicación Streamlit carga datos desde la **misma** base SQLite.
- [ ] Los formularios permiten registrar operaciones y reflejan los cambios en inventario.
- [ ] Los KPI se calculan desde consultas identificables y son reproducibles.
- [ ] Las alertas se generan y consultan desde la aplicación.
- [ ] El README indica versiones y dependencias reales, sin rutas pendientes.
- [ ] No se publican datos personales reales, secretos ni archivos locales de base de datos.
- [ ] Informe, presentación y documentación están incorporados en el repositorio.

## 11. Participantes

**Grupo 6 — P101:** Diego Victoriano, Matías Castro, Ricardo García, Iván González y Héctor Sánchez.

Para una visión general del caso y de ambas entregas, consulta el [README principal](../README.md).
