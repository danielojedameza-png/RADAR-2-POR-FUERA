# 🌿 Radar AGRODASIN — Boletín de Oportunidades del Campo

> **🔗 VER EL PORTAL EN VIVO →**
> **[https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/](https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/)**

Sistema de vigilancia de oportunidades de contratación pública para
asociaciones, productores rurales, piscicultores y organizaciones del
sector agropecuario colombiano.

Datos obtenidos desde **SECOP II – Procesos de Contratación** publicados
en [datos.gov.co](https://www.datos.gov.co/resource/p6dx-8zbt) por
Colombia Compra Eficiente (actualización diaria).

---

## 🖥️ Cómo ver el resultado

### Opción 1 — Portal en línea (GitHub Pages) ⭐ Recomendada

El portal se publica automáticamente en:

**👉 [https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/](https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/)**

Se actualiza solo, todos los días a las **7 am hora Colombia**.
También puede forzar una actualización manual desde la pestaña
**Actions → 🌿 Radar AGRODASIN — Publicar Portal → Run workflow**.

> **Primer uso:** Para que GitHub Pages funcione, active la opción en:
> `Settings → Pages → Source → GitHub Actions`

### Opción 2 — Local (Python)

```bash
# Con datos reales de SECOP II
python -m radar_agrodasin --days 90 --output index.html

# Con datos de muestra (sin internet)
python -m radar_agrodasin --dry-run --output index.html
```

Luego abra `index.html` en su navegador.

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

## Estructura del repositorio

```
radar_agrodasin/
├── __init__.py       # Paquete Python
├── __main__.py       # CLI y datos de muestra
├── config.py         # Palabras clave, territorios, reglas de puntuación
├── fetch.py          # Consulta a la API de Datos Abiertos SECOP II
├── scorer.py         # Motor de relevancia AGRODASIN
└── generator.py      # Generador de HTML estático (3 capas)
.github/
└── workflows/
    └── deploy.yml    # Publicación automática en GitHub Pages
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

## Flujo de actualización automática

El workflow de GitHub Actions se encarga de todo:

```
Cada día a las 7 am Colombia → genera index.html → publica en GitHub Pages
```

Para actualización manual:
1. Ir a **Actions → 🌿 Radar AGRODASIN — Publicar Portal**
2. Clic en **Run workflow**
3. Elegir cuántos días de datos consultar

También puede correr localmente:

```bash
# Datos reales
python -m radar_agrodasin --days 30 --output index.html

# Sin internet
python -m radar_agrodasin --dry-run --output index.html
```

### Opciones del CLI

| Opción | Default | Descripción |
|--------|---------|-------------|
| `--output PATH` | `index.html` | Archivo HTML de salida |
| `--days N` | `90` | Procesos de los últimos N días |
| `--max-records N` | `5000` | Límite de registros a descargar |
| `--dry-run` | — | Usa datos de muestra |
| `--verbose` | — | Logging detallado |

---

## Aviso

Esta herramienta es un apoyo informativo. Verifique siempre la información
directamente en el expediente oficial de SECOP II antes de tomar decisiones.
Colombia Compra Eficiente recomienda validar la veracidad contra los
documentos del proceso cuando algo se vea atípico.
