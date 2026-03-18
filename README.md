# 🌿 Radar AGRODASIN — Boletín de Oportunidades del Campo

Sistema de vigilancia de oportunidades de contratación pública para
asociaciones, productores rurales, piscicultores y organizaciones del
sector agropecuario colombiano.

Datos obtenidos desde **SECOP II – Procesos de Contratación** publicados
en [datos.gov.co](https://www.datos.gov.co/resource/p6dx-8zbt) por
Colombia Compra Eficiente (actualización diaria).

---

## Características

| Capa | Descripción |
|------|-------------|
| **Capa 1 – Listado general** | Todos los procesos activos con buscador y filtros por prioridad |
| **Capa 2 – Recomendadas** | Solo oportunidades de Alta y Media prioridad para AGRODASIN |
| **Capa 3 – Ficha del proceso** | Resumen humano, puntaje, requisitos clave y enlace oficial SECOP II |

### Motor de puntuación AGRODASIN

Cada proceso recibe una puntuación basada en:

- **+Palabras clave** (extensión agropecuaria, piscicultura, asistencia técnica, agricultura familiar, etc.)
- **+Entidades prioritarias** (ADR, SENA, ICBF, alcaldías, gobernaciones, AUNAP…)
- **+Territorios** (Bolívar, Magdalena, Cesar, Sucre, Córdoba, Talaigua Nuevo, Mompox…)
- **−Penalizaciones** (armamento, software especializado, obras hospitalarias…)
- **±Vigencia** (procesos próximos al cierre se priorizan; vencidos se penalizan)

| Etiqueta | Puntaje | Significado |
|----------|---------|-------------|
| 🟢 ALTA | ≥ 70 pts | Revisar de inmediato |
| 🟡 MEDIA | ≥ 40 pts | Revisión técnica recomendada |
| 🟠 BAJA | ≥ 20 pts | Solo informativa |
| 🔴 DESCARTAR | < 20 pts | No aplica para AGRODASIN |

---

## Uso rápido

### Requisitos

- Python 3.9+

### Generar el portal con datos reales de SECOP II

```bash
python -m radar_agrodasin --days 90 --output index.html
```

### Modo demo (sin llamada a la API)

```bash
python -m radar_agrodasin --dry-run --output index.html
```

Abra `index.html` en el navegador para ver el portal.

### Opciones del CLI

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--output PATH` | `index.html` | Archivo HTML de salida |
| `--days N` | `90` | Procesos de los últimos N días |
| `--max-records N` | `5000` | Límite de registros a descargar |
| `--dry-run` | — | Usa datos de muestra |
| `--verbose` | — | Logging detallado |

---

## Estructura del repositorio

```
radar_agrodasin/
├── __init__.py       # Paquete Python
├── __main__.py       # CLI y datos de muestra
├── config.py         # Palabras clave, territorios, reglas de puntuación
├── fetch.py          # Consulta a la API de Datos Abiertos SECOP II
├── scorer.py         # Motor de relevancia AGRODASIN
└── generator.py      # Generador de HTML estático (3 capas)
tests/
└── test_scorer.py    # Pruebas unitarias del motor de puntuación
index.html            # Portal generado (demo con datos de muestra)
requirements.txt
setup.py
```

---

## Fuente de datos

- **SECOP II – Procesos de Contratación**
  `https://www.datos.gov.co/resource/p6dx-8zbt.json`
  Publicado por Colombia Compra Eficiente. Incluye procesos en desarrollo,
  con contrato y sin contrato. Actualización diaria.

- Para revisar documentos y detalles de un proceso específico, use el
  enlace oficial al expediente que aparece en cada ficha del portal.

---

## Flujo de actualización recomendado

```
Lunes    → python -m radar_agrodasin --days 7 --output index.html
Miércoles→ Revisar oportunidades ALTA y publicar en web / WhatsApp
Viernes  → Boletín semanal con top oportunidades
```

---

## Aviso

Esta herramienta es un apoyo informativo. Verifique siempre la información
directamente en el expediente oficial de SECOP II antes de tomar decisiones.
Colombia Compra Eficiente recomienda validar la veracidad contra los
documentos del proceso cuando algo se vea atípico.
