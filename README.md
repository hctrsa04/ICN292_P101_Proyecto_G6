# ICN292 — Proyecto SIG Alta Facha | Grupo 6 (P101)

Repositorio del proyecto aplicado de **Sistemas de Información para la Gestión (ICN292)**, desarrollado por estudiantes de Ingeniería Civil Industrial de la **Universidad Técnica Federico Santa María (UTFSM)**.

El proyecto busca apoyar a **Alta Facha**, microemprendimiento de venta de vestuario femenino, mediante un **Sistema de Información para la Gestión (SIG)** que centralice inventario, ventas y clientes; automatice tareas operativas y facilite el análisis de información comercial.

## 1. La PYME y el problema abordado

Alta Facha comercializa prendas principalmente por **Instagram**, con comunicación directa con sus clientas. Parte de la administración de inventario y ventas se realiza manualmente mediante hojas de cálculo, lo que dificulta mantener un registro actualizado y consultar márgenes e indicadores de gestión.

La solución propuesta es una **aplicación web interna**, con una interfaz sencilla para registrar operaciones y consultar información, conectada a una **base de datos relacional SQLite**. La aplicación se desarrolla con **Python y Streamlit**; la automatización contempla alertas de prendas con baja rotación.

> **Alcance académico:** la Entrega 2 corresponde a un prototipo ejecutable y reproducible en `localhost`. No sustituye los canales de venta, cobro o despacho de Alta Facha.

## 2. Organización del repositorio

| Carpeta | Contenido | Acceso |
|---|---|---|
| **E1/** | Primera entrega: diagnóstico, requerimientos, BPMN, ER preliminar, arquitectura, planificación y documentos enviados. Se conserva como referencia histórica. | [Ver E1](./E1/README.md) |
| **E2/** | Segunda entrega: implementación del SIG, base de datos, aplicación, automatización, documentación, informe y presentación. | [Ver E2](./E2/README.md) |

```text
ICN292_P101_Proyecto_G6/
├── README.md             ← Estás aquí: índice general
├── E1/
│   ├── README.md         ← Documentación de la primera entrega
│   ├── assets/
│   ├── docs/
│   ├── evidencia-pyme/
│   └── informe/
└── E2/
    ├── README.md         ← Guía técnica y de ejecución del SIG
    ├── app/              ← Aplicación web Streamlit
    ├── db/               ← SQLite, scripts SQL y automatización
    ├── docs/             ← Documentación técnica y trazabilidad
    ├── assets/           ← Diagramas y recursos visuales
    ├── informe/          ← Informe final
    └── presentacion/     ← Diapositivas de defensa
```

## 3. Relación entre E1 y E2

- **E1 — Diseño:** se documentó la situación de la PYME, el problema, los requisitos, los modelos de procesos y datos, y la arquitectura propuesta.
- **E2 — Implementación:** se actualiza el diseño con la retroalimentación recibida y se materializa una solución local con base de datos, consultas, interfaz, KPI y automatización.

Los cambios relevantes entre ambas entregas se documentarán en **E2/docs/** y en el registro de cambios correspondiente.

## 4. Integrantes y áreas de trabajo

| Integrante | Área principal en el proyecto |
|---|---|
| **Diego Victoriano** | Coordinación general, arquitectura, aplicación Streamlit e integración |
| **Matías Castro** | Informe, gobernanza de datos y documentación |
| **Ricardo García** | Contexto PYME, evidencia, indicadores y trazabilidad |
| **Iván González** | Requerimientos, procesos BPMN, apoyo SQL y automatización |
| **Héctor Sánchez** | Modelo relacional, base SQL y apoyo al repositorio |

*La distribución refleja las áreas de trabajo del equipo y puede ajustarse en la documentación final.*

## 5. Cómo ejecutar la solución

Las **instrucciones de instalación, carga de la base, ejecución en localhost y verificación** están en el [README de la Entrega 2](./E2/README.md). Esta página es solo el índice general del repositorio.

## 6. Referencias

- [Repositorio del proyecto en GitHub](https://github.com/hctrsa04/ICN292_P101_Proyecto_G6)
- [Plataforma Aula USM](https://aula.usm.cl/)

**Nota sobre datos:** la documentación pública y los datos de prueba no deben contener información personal de clientas ni datos comerciales confidenciales sin tratamiento adecuado.
