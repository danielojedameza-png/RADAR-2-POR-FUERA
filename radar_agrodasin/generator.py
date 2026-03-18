"""
Generador del sitio estático del Radar AGRODASIN.

Produce un archivo index.html autónomo que contiene:
  Capa 1 – Listado general de oportunidades activas
  Capa 2 – Oportunidades recomendadas (ALTA y MEDIA prioridad)
  Capa 3 – Fichas detalladas por proceso (modal emergente)

Todo el estilo y la lógica de búsqueda/filtro están embebidos en el
propio HTML para facilitar la publicación como sitio estático.
"""

from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone
from typing import Any

from . import config

# ---------------------------------------------------------------------------
# Helpers de formato
# ---------------------------------------------------------------------------

def _fmt_currency(value: Any) -> str:
    try:
        n = float(value)
        return f"${n:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "No disponible"


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso[:10])
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return iso[:10]


def _priority_badge(priority: str) -> str:
    classes = {
        config.PRIORIDAD_ALTA: "badge-alta",
        config.PRIORIDAD_MEDIA: "badge-media",
        config.PRIORIDAD_BAJA: "badge-baja",
        config.PRIORIDAD_DESCARTAR: "badge-descartar",
    }
    cls = classes.get(priority, "badge-baja")
    return f'<span class="badge {cls}">{html.escape(priority)}</span>'


def _aplica_badge(aplica: str) -> str:
    if "REVISAR YA" in aplica:
        return f'<span class="badge badge-alta">{html.escape(aplica)}</span>'
    if "REVISIÓN" in aplica:
        return f'<span class="badge badge-media">{html.escape(aplica)}</span>'
    if "INFORMATIVA" in aplica:
        return f'<span class="badge badge-baja">{html.escape(aplica)}</span>'
    return f'<span class="badge badge-descartar">{html.escape(aplica)}</span>'


def _short_object(text: str, max_len: int = 80) -> str:
    text = text.strip()
    if len(text) > max_len:
        return text[:max_len].rstrip() + "…"
    return text


# ---------------------------------------------------------------------------
# Construcción de secciones HTML
# ---------------------------------------------------------------------------

def _build_card(rec: dict) -> str:
    """Genera una tarjeta de proceso para la vista de tabla."""
    proceso_id = html.escape(str(rec.get("id_del_portafolio", "")))
    ref = html.escape(str(rec.get("referencia_del_proceso", "S/N")))
    entidad = html.escape(str(rec.get("nombre_de_la_entidad", "—")))
    objeto = html.escape(_short_object(str(rec.get("nombre_del_procedimiento", "—"))))
    depto = html.escape(str(rec.get("departamento", "—")))
    ciudad = html.escape(str(rec.get("ciudad", "—")))
    estado = html.escape(str(rec.get("estado_del_procedimiento", "—")))
    modalidad = html.escape(str(rec.get("modalidad_de_contratacion", "—")))
    valor = _fmt_currency(rec.get("valor_total_estimado"))
    fecha_pub = _fmt_date(rec.get("fecha_de_publicacion_del"))
    fecha_cierre = _fmt_date(rec.get("fecha_limite_de_recepcion"))
    url_proceso = html.escape(str(rec.get("urlproceso", "#")))
    priority = rec.get("nivel_prioridad", config.PRIORIDAD_BAJA)
    aplica = rec.get("aplica_agrodasin", "NO")
    categorias = ", ".join(rec.get("categorias_detectadas", []))
    publico = html.escape(str(rec.get("publico_objetivo", "General")))
    puntaje = rec.get("puntaje_total", 0)

    return f"""
    <tr class="process-row" data-priority="{html.escape(priority)}"
        data-text="{objeto.lower()} {entidad.lower()} {depto.lower()}"
        onclick="showDetail('{proceso_id}')">
      <td>{_priority_badge(priority)}</td>
      <td><small class="text-muted">{ref}</small><br><strong>{objeto}</strong>
          {(f'<br><small class="text-muted">🏷 {html.escape(categorias)}</small>') if categorias else ''}
      </td>
      <td>{entidad}<br><small class="text-muted">{depto} / {ciudad}</small></td>
      <td><span class="estado-chip">{estado}</span><br><small>{modalidad}</small></td>
      <td class="text-end"><strong>{valor}</strong></td>
      <td>{fecha_pub}</td>
      <td><strong>{fecha_cierre}</strong></td>
      <td>{_aplica_badge(aplica)}<br><small>👥 {publico}</small></td>
      <td>
        <a href="{url_proceso}" target="_blank" rel="noopener noreferrer"
           class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation()">
          Ver expediente
        </a>
      </td>
    </tr>"""


def _build_summary_card(rec: dict) -> str:
    """Tarjeta compacta para la capa de oportunidades recomendadas."""
    entidad = html.escape(str(rec.get("nombre_de_la_entidad", "—")))
    ref = html.escape(str(rec.get("referencia_del_proceso", "S/N")))
    objeto = html.escape(_short_object(str(rec.get("nombre_del_procedimiento", "—")), 100))
    depto = html.escape(str(rec.get("departamento", "—")))
    ciudad = html.escape(str(rec.get("ciudad", "")))
    valor = _fmt_currency(rec.get("valor_total_estimado"))
    fecha_cierre = _fmt_date(rec.get("fecha_limite_de_recepcion"))
    url_proceso = html.escape(str(rec.get("urlproceso", "#")))
    priority = rec.get("nivel_prioridad", config.PRIORIDAD_BAJA)
    aplica = rec.get("aplica_agrodasin", "NO")
    categorias = ", ".join(rec.get("categorias_detectadas", []))
    publico = html.escape(str(rec.get("publico_objetivo", "General")))
    proceso_id = html.escape(str(rec.get("id_del_portafolio", "")))

    border_color = "#28a745" if priority == config.PRIORIDAD_ALTA else "#ffc107"

    return f"""
    <div class="col-md-6 col-lg-4 mb-3">
      <div class="card summary-card h-100" style="border-left: 4px solid {border_color};"
           onclick="showDetail('{proceso_id}')" role="button">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-2">
            {_priority_badge(priority)}
            <small class="text-muted">{ref}</small>
          </div>
          <h6 class="card-title">{objeto}</h6>
          <p class="card-text mb-1"><strong>Entidad:</strong> {entidad}</p>
          <p class="card-text mb-1"><strong>Territorio:</strong> {depto}{f' / {ciudad}' if ciudad else ''}</p>
          <p class="card-text mb-1"><strong>Valor:</strong> {valor}</p>
          <p class="card-text mb-2"><strong>Cierre:</strong> {fecha_cierre}</p>
          {f'<p class="card-text mb-1"><small>🏷 {html.escape(categorias)}</small></p>' if categorias else ''}
          <p class="card-text mb-2"><small>👥 {publico}</small></p>
          <div class="d-flex gap-2">
            {_aplica_badge(aplica)}
            <a href="{url_proceso}" target="_blank" rel="noopener noreferrer"
               class="btn btn-sm btn-success ms-auto" onclick="event.stopPropagation()">
              Ver proceso
            </a>
          </div>
        </div>
      </div>
    </div>"""


def _build_detail_modal_data(records: list[dict]) -> str:
    """Serializa los registros como JSON para el modal de detalle."""
    detail_map = {}
    for rec in records:
        pid = str(rec.get("id_del_portafolio", ""))
        if not pid:
            continue
        detail_map[pid] = {
            "referencia": rec.get("referencia_del_proceso", "S/N"),
            "entidad": rec.get("nombre_de_la_entidad", "—"),
            "nit": rec.get("nit_entidad", "—"),
            "objeto": rec.get("nombre_del_procedimiento", "—"),
            "descripcion": (rec.get("descripcion_del_procedimiento") or "")[:500],
            "departamento": rec.get("departamento", "—"),
            "ciudad": rec.get("ciudad", "—"),
            "estado": rec.get("estado_del_procedimiento", "—"),
            "modalidad": rec.get("modalidad_de_contratacion", "—"),
            "valor": _fmt_currency(rec.get("valor_total_estimado")),
            "fecha_publicacion": _fmt_date(rec.get("fecha_de_publicacion_del")),
            "fecha_cierre": _fmt_date(rec.get("fecha_limite_de_recepcion")),
            "unspsc": rec.get("codigo_unspsc", "—"),
            "url": rec.get("urlproceso", "#"),
            "prioridad": rec.get("nivel_prioridad", config.PRIORIDAD_BAJA),
            "aplica": rec.get("aplica_agrodasin", "NO"),
            "categorias": rec.get("categorias_detectadas", []),
            "publico": rec.get("publico_objetivo", "General"),
            "puntaje": rec.get("puntaje_total", 0),
        }
    return json.dumps(detail_map, ensure_ascii=False)


# ---------------------------------------------------------------------------
# HTML principal
# ---------------------------------------------------------------------------

def generate_html(records: list[dict], output_path: str = "index.html") -> None:
    """
    Genera el archivo index.html completo con los datos del radar.

    :param records: Lista de registros ya puntuados (salida de scorer.py).
    :param output_path: Ruta del archivo HTML a generar.
    """
    fecha_corte = datetime.now(tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    total = len(records)
    alta = sum(1 for r in records if r.get("nivel_prioridad") == config.PRIORIDAD_ALTA)
    media = sum(1 for r in records if r.get("nivel_prioridad") == config.PRIORIDAD_MEDIA)
    baja = sum(1 for r in records if r.get("nivel_prioridad") == config.PRIORIDAD_BAJA)
    descartar = total - alta - media - baja

    recommended = [
        r for r in records
        if r.get("nivel_prioridad") in (config.PRIORIDAD_ALTA, config.PRIORIDAD_MEDIA)
    ]

    table_rows = "\n".join(_build_card(r) for r in records)
    summary_cards = "\n".join(_build_summary_card(r) for r in recommended)
    detail_json = _build_detail_modal_data(records)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Radar AGRODASIN – Oportunidades del Campo</title>
  <!-- Favicon inline (SVG) — evita el error 404 en GET /favicon.ico -->
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='16' fill='%231a6b3c'/%3E%3Ctext x='16' y='22' font-size='18' text-anchor='middle' fill='white'%3E%F0%9F%8C%BF%3C/text%3E%3C/svg%3E">
  <!-- Meta Open Graph — imagen de previsualización para redes sociales -->
  <meta property="og:title" content="Radar AGRODASIN – Oportunidades del Campo">
  <meta property="og:description" content="Procesos de contratación pública relevantes para el sector agropecuario colombiano — datos desde SECOP II.">
  <meta property="og:image" content="https://danielojedameza-png.github.io/RADAR-2-POR-FUERA/og-image.svg">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
        rel="stylesheet"
        crossorigin="anonymous">
  <style>
    :root {{
      --color-alta: #28a745;
      --color-media: #ffc107;
      --color-baja: #fd7e14;
      --color-descartar: #dc3545;
    }}
    body {{ background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }}
    .navbar-brand {{ font-weight: 700; font-size: 1.3rem; }}
    .hero {{ background: linear-gradient(135deg, #1a6b3c 0%, #2d9e5f 100%);
             color: white; padding: 2rem 0; }}
    .hero h1 {{ font-size: 2rem; font-weight: 700; }}
    .stat-card {{ border-radius: 12px; padding: 1.2rem; text-align: center;
                  box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
    .stat-card h2 {{ font-size: 2.5rem; font-weight: 700; margin: 0; }}
    .badge-alta {{ background: var(--color-alta); color: white; }}
    .badge-media {{ background: var(--color-media); color: #212529; }}
    .badge-baja {{ background: var(--color-baja); color: white; }}
    .badge-descartar {{ background: var(--color-descartar); color: white; }}
    .badge {{ display: inline-block; padding: .3em .6em; border-radius: .4em;
              font-size: .78em; font-weight: 600; }}
    .estado-chip {{ background: #e9ecef; border-radius: 4px; padding: 2px 6px;
                    font-size: .8em; }}
    .summary-card {{ transition: transform .2s, box-shadow .2s; cursor: pointer; }}
    .summary-card:hover {{ transform: translateY(-3px);
                           box-shadow: 0 6px 20px rgba(0,0,0,.15); }}
    .process-row {{ cursor: pointer; transition: background .15s; }}
    .process-row:hover {{ background: #e8f5e9 !important; }}
    .tab-content {{ padding-top: 1.5rem; }}
    #searchBox {{ border-radius: 8px; }}
    .modal-header-alta {{ background: var(--color-alta); color: white; }}
    .modal-header-media {{ background: var(--color-media); color: #212529; }}
    .modal-header-baja {{ background: var(--color-baja); color: white; }}
    .modal-header-descartar {{ background: var(--color-descartar); color: white; }}
    .ficha-label {{ font-weight: 600; color: #495057; font-size: .85em;
                    text-transform: uppercase; letter-spacing: .05em; }}
    footer {{ background: #1a6b3c; color: white; padding: 1.5rem 0; margin-top: 3rem; }}
    @media (max-width: 768px) {{
      .table-responsive {{ font-size: .85rem; }}
    }}
  </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-dark" style="background:#1a6b3c;">
  <div class="container-fluid">
    <span class="navbar-brand">🌿 Radar AGRODASIN</span>
    <span class="text-white-50 small">Actualizado: {fecha_corte}</span>
  </div>
</nav>

<!-- Hero -->
<section class="hero">
  <div class="container">
    <h1>🌾 Boletín de Oportunidades del Campo</h1>
    <p class="lead mb-3">Procesos de contratación pública relevantes para
    asociaciones, productores rurales y organizaciones del sector agropecuario
    colombiano — datos desde SECOP II / Datos Abiertos Colombia.</p>

    <!-- Estadísticas -->
    <div class="row g-3">
      <div class="col-6 col-md-3">
        <div class="stat-card bg-white text-dark">
          <h2>{total}</h2>
          <small>Total activos</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="stat-card" style="background:var(--color-alta);color:white">
          <h2>{alta}</h2>
          <small>Alta prioridad</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="stat-card" style="background:var(--color-media);color:#212529">
          <h2>{media}</h2>
          <small>Media prioridad</small>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="stat-card" style="background:var(--color-baja);color:white">
          <h2>{baja}</h2>
          <small>Baja prioridad</small>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Contenido principal -->
<div class="container mt-4">

  <!-- Tabs de las 3 capas -->
  <ul class="nav nav-tabs" id="mainTab" role="tablist">
    <li class="nav-item">
      <button class="nav-link active" data-bs-toggle="tab"
              data-bs-target="#tab-recomendadas" type="button">
        ⭐ Recomendadas ({len(recommended)})
      </button>
    </li>
    <li class="nav-item">
      <button class="nav-link" data-bs-toggle="tab"
              data-bs-target="#tab-listado" type="button">
        📋 Listado general ({total})
      </button>
    </li>
    <li class="nav-item">
      <button class="nav-link" data-bs-toggle="tab"
              data-bs-target="#tab-info" type="button">
        ℹ️ Acerca del Radar
      </button>
    </li>
  </ul>

  <div class="tab-content" id="mainTabContent">

    <!-- CAPA 2: Oportunidades recomendadas -->
    <div class="tab-pane fade show active" id="tab-recomendadas">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0">Oportunidades de alta y media prioridad para AGRODASIN</h5>
        <span class="badge badge-alta">{len(recommended)} procesos</span>
      </div>
      {'<div class="alert alert-warning">No hay oportunidades recomendadas en este momento. Intenta ampliar el rango de fechas de búsqueda.</div>' if not recommended else ''}
      <div class="row">
        {summary_cards}
      </div>
    </div>

    <!-- CAPA 1: Listado general -->
    <div class="tab-pane fade" id="tab-listado">
      <!-- Buscador y filtros -->
      <div class="row g-2 mb-3">
        <div class="col-md-5">
          <input type="text" id="searchBox" class="form-control"
                 placeholder="🔍 Buscar por objeto, entidad o territorio…"
                 oninput="filterTable()">
        </div>
        <div class="col-md-3">
          <select id="filterPriority" class="form-select" onchange="filterTable()">
            <option value="">Todas las prioridades</option>
            <option value="ALTA">Alta prioridad</option>
            <option value="MEDIA">Media prioridad</option>
            <option value="BAJA">Baja prioridad</option>
            <option value="DESCARTAR">Descartar</option>
          </select>
        </div>
        <div class="col-md-2">
          <button class="btn btn-outline-secondary w-100" onclick="resetFilters()">
            Limpiar
          </button>
        </div>
        <div class="col-md-2 text-end">
          <span id="rowCount" class="text-muted small pt-2 d-inline-block"></span>
        </div>
      </div>

      <div class="table-responsive">
        <table class="table table-hover table-sm align-middle" id="processTable">
          <thead class="table-dark">
            <tr>
              <th>Prioridad</th>
              <th>Objeto del proceso</th>
              <th>Entidad / Territorio</th>
              <th>Estado / Modalidad</th>
              <th class="text-end">Valor</th>
              <th>Publicado</th>
              <th>Cierre</th>
              <th>Aplica AGRODASIN</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="tableBody">
            {table_rows}
          </tbody>
        </table>
      </div>
      {'<div class="alert alert-info text-center">No se encontraron procesos activos en este momento.</div>' if not records else ''}
    </div>

    <!-- Acerca del Radar -->
    <div class="tab-pane fade" id="tab-info">
      <div class="row">
        <div class="col-md-8">
          <h5>¿Qué es el Radar AGRODASIN?</h5>
          <p>El Radar AGRODASIN es una herramienta de vigilancia de oportunidades de
          contratación pública relevantes para el sector agropecuario, asociaciones
          campesinas, piscicultores y organizaciones rurales de Colombia.</p>

          <h6>Fuente de datos</h6>
          <p>Todos los procesos provienen del conjunto de datos oficial
          <strong>SECOP II – Procesos de Contratación</strong> publicado en
          <a href="https://www.datos.gov.co/resource/p6dx-8zbt" target="_blank"
             rel="noopener noreferrer">datos.gov.co</a>
          por Colombia Compra Eficiente. Los datos se actualizan diariamente.</p>

          <h6>Cómo se calcula la prioridad</h6>
          <ul>
            <li><strong class="text-success">ALTA (≥70 pts):</strong>
                Proceso directamente relacionado con el sector AGRODASIN en territorios
                prioritarios.</li>
            <li><strong class="text-warning">MEDIA (≥40 pts):</strong>
                Proceso relevante que conviene revisar técnicamente.</li>
            <li><strong class="text-warning" style="color:var(--color-baja)!important">
                BAJA (≥20 pts):</strong>
                Solo informativo; evaluar si aplica.</li>
            <li><strong class="text-danger">DESCARTAR (&lt;20 pts):</strong>
                No parece relevante para AGRODASIN.</li>
          </ul>

          <h6>Territorios prioritarios</h6>
          <p>Bolívar, Magdalena, Cesar, Sucre, Córdoba, Atlántico, La Guajira,
          Talaigua Nuevo, Mompox, Santa Marta y el Caribe colombiano.</p>

          <h6>Sectores vigilados</h6>
          <ul>
            <li>Extensión agropecuaria y asistencia técnica</li>
            <li>Piscicultura y acuicultura</li>
            <li>Agricultura familiar y economía campesina</li>
            <li>Fortalecimiento de asociaciones y cooperativas</li>
            <li>Formación, capacitación y talleres rurales</li>
            <li>Compras públicas locales y mercados campesinos</li>
            <li>Medio ambiente, reforestación y viveros</li>
          </ul>

          <div class="alert alert-warning mt-3">
            <strong>⚠️ Aviso importante:</strong> Esta herramienta es un apoyo
            informativo. Siempre verifique la información directamente en el expediente
            oficial de SECOP II antes de tomar decisiones. Colombia Compra Eficiente
            recomienda validar la veracidad contra los documentos del proceso cuando
            algo se vea atípico.
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-header bg-success text-white">
              <strong>📊 Estadísticas del corte</strong>
            </div>
            <div class="card-body">
              <p><strong>Fecha:</strong> {fecha_corte}</p>
              <p><strong>Total procesos activos:</strong> {total}</p>
              <p><strong class="text-success">Alta prioridad:</strong> {alta}</p>
              <p><strong style="color:var(--color-media)">Media prioridad:</strong>
                 {media}</p>
              <p><strong style="color:var(--color-baja)">Baja prioridad:</strong>
                 {baja}</p>
              <p><strong class="text-danger">Descartar:</strong> {descartar}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- CAPA 3: Modal de detalle del proceso -->
<div class="modal fade" id="detailModal" tabindex="-1">
  <div class="modal-dialog modal-lg modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header" id="detailModalHeader">
        <h5 class="modal-title" id="detailModalTitle">Detalle del proceso</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body" id="detailModalBody">
        <!-- contenido dinámico -->
      </div>
      <div class="modal-footer">
        <a id="detailModalLink" href="#" target="_blank" rel="noopener noreferrer"
           class="btn btn-success">
          🔗 Ver expediente oficial en SECOP II
        </a>
        <button type="button" class="btn btn-secondary"
                data-bs-dismiss="modal">Cerrar</button>
      </div>
    </div>
  </div>
</div>

<footer>
  <div class="container text-center">
    <p class="mb-1">🌿 <strong>Radar AGRODASIN</strong> — Boletín de Oportunidades del
    Campo</p>
    <p class="mb-0 text-white-50 small">Datos: Colombia Compra Eficiente / SECOP II –
    datos.gov.co | Actualización diaria</p>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"
        crossorigin="anonymous">
</script>
<script>
  // Datos de detalle embebidos
  const DETAIL_DATA = {detail_json};

  function showDetail(pid) {{
    const d = DETAIL_DATA[pid];
    if (!d) return;

    const headerEl = document.getElementById('detailModalHeader');
    const titleEl  = document.getElementById('detailModalTitle');
    const bodyEl   = document.getElementById('detailModalBody');
    const linkEl   = document.getElementById('detailModalLink');

    const priorityClass = {{
      'ALTA': 'modal-header-alta',
      'MEDIA': 'modal-header-media',
      'BAJA': 'modal-header-baja',
      'DESCARTAR': 'modal-header-descartar',
    }}[d.prioridad] || 'modal-header-baja';

    headerEl.className = 'modal-header ' + priorityClass;
    titleEl.textContent = d.objeto;
    linkEl.href = d.url;

    const cats = Array.isArray(d.categorias) ? d.categorias.join(', ') : '';

    bodyEl.innerHTML = `
      <div class="row g-3">
        <div class="col-md-6">
          <p class="ficha-label">Entidad compradora</p>
          <p>${{escHtml(d.entidad)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Número del proceso</p>
          <p>${{escHtml(d.referencia)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Departamento / Municipio</p>
          <p>${{escHtml(d.departamento)}} / ${{escHtml(d.ciudad)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Modalidad de contratación</p>
          <p>${{escHtml(d.modalidad)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Valor estimado</p>
          <p><strong>${{escHtml(d.valor)}}</strong></p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Estado</p>
          <p>${{escHtml(d.estado)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Fecha de publicación</p>
          <p>${{escHtml(d.fecha_publicacion)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">Fecha límite de recepción</p>
          <p><strong>${{escHtml(d.fecha_cierre)}}</strong></p>
        </div>
        ${{cats ? `<div class="col-12"><p class="ficha-label">Categorías detectadas</p>
          <p>${{escHtml(cats)}}</p></div>` : ''}}
        <div class="col-md-6">
          <p class="ficha-label">Público objetivo</p>
          <p>${{escHtml(d.publico)}}</p>
        </div>
        <div class="col-md-6">
          <p class="ficha-label">UNSPSC</p>
          <p>${{escHtml(d.unspsc)}}</p>
        </div>
        ${{d.descripcion ? `<div class="col-12">
          <p class="ficha-label">Descripción</p>
          <p class="text-muted small">${{escHtml(d.descripcion)}}${{d.descripcion.length >= 500 ? '…' : ''}}</p>
        </div>` : ''}}
        <div class="col-12">
          <hr>
          <p class="ficha-label">Alerta rápida AGRODASIN</p>
          <div class="alert ${{d.prioridad === 'ALTA' ? 'alert-success' :
                               d.prioridad === 'MEDIA' ? 'alert-warning' :
                               d.prioridad === 'BAJA' ? 'alert-secondary' : 'alert-danger'}}">
            <strong>${{escHtml(d.aplica)}}</strong> — Puntaje: ${{d.puntaje}} pts
          </div>
        </div>
      </div>`;

    new bootstrap.Modal(document.getElementById('detailModal')).show();
  }}

  function escHtml(str) {{
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }}

  function filterTable() {{
    const query  = document.getElementById('searchBox').value.toLowerCase();
    const priori = document.getElementById('filterPriority').value;
    const rows   = document.querySelectorAll('#tableBody .process-row');
    let visible  = 0;

    rows.forEach(row => {{
      const text     = row.dataset.text || '';
      const priority = row.dataset.priority || '';
      const matchTxt = !query || text.includes(query);
      const matchPri = !priori || priority === priori;
      if (matchTxt && matchPri) {{
        row.style.display = '';
        visible++;
      }} else {{
        row.style.display = 'none';
      }}
    }});

    document.getElementById('rowCount').textContent =
      `Mostrando ${{visible}} de ${{rows.length}}`;
  }}

  function resetFilters() {{
    document.getElementById('searchBox').value = '';
    document.getElementById('filterPriority').value = '';
    filterTable();
  }}

  // Inicializar contador
  filterTable();
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(html_content)
