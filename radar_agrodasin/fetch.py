"""
Módulo de consulta a la API de Datos Abiertos de SECOP II.

Usa el endpoint Socrata de datos.gov.co para obtener procesos de
contratación. Aplica filtros básicos por estado antes de devolver los
registros para reducir el volumen de datos a procesar.
"""

from __future__ import annotations

import logging
import time
import urllib.parse
import urllib.request
import json
from datetime import datetime, timezone
from typing import Iterator

from . import config

logger = logging.getLogger(__name__)


def _build_url(
    offset: int = 0,
    limit: int = config.SECOP_PAGE_LIMIT,
    extra_where: str | None = None,
) -> str:
    """Construye la URL de consulta con parámetros Socrata ($query SoQL)."""
    fields = ",".join(config.SECOP_FIELDS)

    # Filtrar por estados activos para evitar traer todo el historial
    active_quoted = ", ".join(f"'{s}'" for s in config.ACTIVE_STATES)
    where = f"lower(estado_del_procedimiento) in ({active_quoted})"
    if extra_where:
        where = f"({where}) AND ({extra_where})"

    params = {
        "$select": fields,
        "$where": where,
        "$limit": str(limit),
        "$offset": str(offset),
        "$order": "fecha_de_publicacion_del DESC",
    }
    return config.SECOP_API_URL + "?" + urllib.parse.urlencode(params)


def fetch_page(
    offset: int = 0,
    limit: int = config.SECOP_PAGE_LIMIT,
    extra_where: str | None = None,
    timeout: int = 30,
) -> list[dict]:
    """Descarga una página de resultados desde la API de SECOP II."""
    url = _build_url(offset=offset, limit=limit, extra_where=extra_where)
    logger.debug("GET %s", url)
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "RadarAGRODASIN/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
    return json.loads(raw)


def fetch_all(
    max_records: int = 5000,
    extra_where: str | None = None,
    delay_between_pages: float = 1.0,
) -> list[dict]:
    """
    Descarga todos los registros activos de SECOP II respetando la
    paginación de Socrata.

    :param max_records: Límite absoluto de registros a descargar.
    :param extra_where: Condición SoQL adicional (p. ej. filtro de fecha).
    :param delay_between_pages: Segundos de espera entre páginas.
    :return: Lista de dicts con los registros crudos.
    """
    records: list[dict] = []
    offset = 0
    limit = config.SECOP_PAGE_LIMIT

    while offset < max_records:
        batch_limit = min(limit, max_records - offset)
        try:
            page = fetch_page(
                offset=offset, limit=batch_limit, extra_where=extra_where
            )
        except Exception as exc:
            logger.error("Error al descargar página offset=%d: %s", offset, exc)
            break

        records.extend(page)
        logger.info("Descargados %d registros (total acumulado: %d)", len(page), len(records))

        if len(page) < batch_limit:
            # No hay más páginas
            break

        offset += batch_limit
        if offset < max_records:
            time.sleep(delay_between_pages)

    return records


def build_recent_filter(days: int = 90) -> str:
    """Devuelve un filtro SoQL para limitar registros por fecha de publicación."""
    cutoff = datetime.now(tz=timezone.utc)
    # Socrata acepta fechas ISO 8601
    cutoff_str = cutoff.strftime("%Y-%m-%dT00:00:00")
    # Resta aproximada en días usando fecha directa no es trivial en SoQL;
    # se usa una fecha literal calculada en Python.
    from datetime import timedelta
    since = cutoff - timedelta(days=days)
    since_str = since.strftime("%Y-%m-%dT00:00:00")
    return f"fecha_de_publicacion_del >= '{since_str}'"
