# 🌿 Radar AGRODASIN — Boletín de Oportunidades del Campo

> **🔗 VER EL PORTAL EN VIVO →**
> **[https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/](https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/)**

---

## ⚡ ¿Dónde estás ahora? — Encuentra tu paso

| Lo que ves | Qué hacer |
|------------|-----------|
| Settings → Pages muestra *"Upgrade or make this repository public"* | 👉 [Paso 1 — Hacer repo público](#paso-1--hacer-el-repositorio-público) |
| Settings → Pages muestra fuente = **Acciones de GitHub** pero ofrece botones "Configurar" (Jekyll / HTML estático) | 👉 [Paso 3 — Fusionar el PR](#paso-3--fusionar-la-pull-request-a-main-) ← **NO hacer clic en esos botones** |
| Actions → solo aparece "Copilot coding agent", sin "🌿 Radar AGRODASIN" | 👉 [Paso 3 — Fusionar el PR](#paso-3--fusionar-la-pull-request-a-main-) |
| Actions → aparece "🌿 Radar AGRODASIN" con ✅ verde | ✅ **Portal publicado** — visita el [enlace](#listo-el-portal-está-en-línea-en) |

---

Sistema de vigilancia de oportunidades de contratación pública para
asociaciones, productores rurales, piscicultores y organizaciones del
sector agropecuario colombiano.

Datos obtenidos desde **SECOP II – Procesos de Contratación** publicados
en [datos.gov.co](https://www.datos.gov.co/resource/p6dx-8zbt) por
Colombia Compra Eficiente (actualización diaria).

---

## 🖥️ Cómo ver el resultado

### ⚠️ El repositorio es privado — GitHub Pages no funciona en repositorios privados gratuitos

Cuando entras a **Settings → Pages** y ves el mensaje
*"Upgrade or make this repository public to enable Pages"*,
significa que el repositorio es **privado** y GitHub Pages requiere una de estas dos acciones:

---

### Solución A — Hacer el repositorio público ⭐ Recomendada

> **💡 ¿Por qué no aparece el workflow de Radar en la pestaña Actions?**
> Porque el workflow vive en esta PR y aún no ha sido fusionado a `main`.
> GitHub solo ejecuta workflows de la rama **principal (main)**.
> Sigue los 4 pasos en orden y el portal se publicará automáticamente al fusionar.

---

#### Paso 1 — Hacer el repositorio público

1. Ir al repositorio **`RADAR-2-POR-FUERA`** en GitHub
2. Clic en la pestaña **`Settings`** (engranaje ⚙️, última pestaña del menú superior)
3. En el menú lateral izquierdo, clic en **`General`** (primera opción)
4. Bajar hasta el final de la página hasta la sección roja **"Danger Zone"**
5. Clic en el botón **`Change repository visibility`**
6. En el cuadro que aparece, seleccionar **`Make public`**
7. Clic en **`I want to make this repository public`**
8. Escribir en el campo de texto:
   ```
   RADAR-2-POR-FUERA
   ```
9. Clic en el botón rojo **`I understand, change repository visibility`**
10. GitHub confirmará: *"This repository is now public"* ✅

#### Paso 2 — Activar GitHub Pages

1. Seguir en **Settings** → menú lateral → sección **"Code and automation"** → clic en **`Páginas`** (o **`Pages`**)
2. Ahora ya **no aparece** el mensaje *"Upgrade or make this repository public"*
3. En **"Compilación e implementación"** (o **"Build and deployment"**) → **"Fuente"** → seleccionar **`Acciones de GitHub`** (o **`GitHub Actions`**)
4. Clic en **`Save`** si aparece el botón ✅

> **⚠️ IMPORTANTE: NO hacer clic en "Configurar" de Jekyll ni de "HTML estático"**
> Verás dos tarjetas: *"GitHub Pages Jekyll"* y *"HTML estático"*. **Ignóralas por completo.**
> Esos son plantillas genéricas de GitHub. El workflow del Radar ya está listo en la PR.
> Hacer clic en "Configurar" crearía un workflow diferente e innecesario.

#### ✅ Si ya completaste los Pasos 1 y 2 — ir directamente al Paso 3

#### Paso 3 — Fusionar la Pull Request a main 🚀

> **Este es el último paso y el más importante.**
> Al fusionar, el workflow `🌿 Radar AGRODASIN` llega a `main` y se ejecuta automáticamente.
> El portal quedará publicado en ~2 minutos **sin necesidad de hacer nada más**.

**¿Por qué Actions solo muestra "Copilot coding agent" y no "🌿 Radar AGRODASIN"?**
Porque el workflow del Radar vive en la Pull Request y todavía no ha llegado a `main`.
GitHub solo lista y ejecuta workflows que están en la rama principal.

**Pasos exactos:**

1. Clic en la pestaña **`Pull requests`** (menú superior del repositorio, entre "Issues" y "Actions")
2. Verás una PR llamada **"Fix: workflow hard-fails on private repo…"** — hacer clic en ella
3. Si la PR muestra un banner gris **"This pull request is still a draft"**:
   - Clic en el botón **`Ready for review`** (al pie de la página)
4. Ahora clic en el botón verde **`Merge pull request`**
5. Clic en **`Confirm merge`**
6. ✅ ¡Listo! Ir a la pestaña **`Actions`** — ahora sí aparece **`🌿 Radar AGRODASIN — Publicar Portal`** ejecutándose
7. Esperar ~2 minutos hasta que aparezca el ✅ verde

#### ¡Listo! El portal está en línea en:

**👉 [https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/](https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/)**

Se actualiza automáticamente todos los días a las **7 am hora Colombia**.

---

### Solución B — Descargar el portal desde Actions (sin hacer el repo público)

El workflow siempre genera el portal y lo sube como **artefacto descargable**, aunque el repositorio sea privado:

1. Ir a la pestaña **Actions**
2. Clic en el último workflow **"🌿 Radar AGRODASIN — Publicar Portal"**
3. Si no hay ejecuciones aún, clic en **"Run workflow"** para lanzarlo manualmente
4. Al finalizar, buscar la sección **Artifacts** al pie de la página
5. Descargar **`radar-agrodasin-portal`** (archivo `.zip`)
6. Descomprimir y abrir **`index.html`** en el navegador

---

### Solución C — Local (Python)

```bash
# Con datos reales de SECOP II
python -m radar_agrodasin --days 90 --output index.html

# Con datos de muestra (sin internet)
python -m radar_agrodasin --dry-run --output index.html
```

Luego abrir `index.html` en el navegador.

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
