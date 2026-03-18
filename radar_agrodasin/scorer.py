"""
Motor de puntuación de relevancia AGRODASIN.

Toma un registro crudo de SECOP II y calcula:
- puntaje_palabras_clave
- puntaje_entidad
- puntaje_territorio
- penalizacion_descarte
- puntaje_vigencia
- puntaje_total
- nivel_prioridad
- aplica_agrodasin
- categorias_detectadas   (lista de categorías temáticas encontradas)
- publico_objetivo        (inferido del objeto y descripción)
"""

from __future__ import annotations

import unicodedata
from datetime import date, datetime
from typing import Any

from . import config


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Convierte a minúsculas y elimina tildes para comparación robusta."""
    nfkd = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _combined_text(record: dict) -> str:
    """Une los campos de texto relevantes en un solo string normalizado."""
    fields = [
        record.get("nombre_de_la_entidad", ""),
        record.get("nombre_del_procedimiento", ""),
        record.get("descripcion_del_procedimiento", ""),
        record.get("departamento", ""),
        record.get("ciudad", ""),
        record.get("modalidad_de_contratacion", ""),
        record.get("estado_del_procedimiento", ""),
        record.get("codigo_unspsc", ""),
    ]
    return _normalize(" ".join(str(f) for f in fields if f))


# ---------------------------------------------------------------------------
# Cálculo de puntajes individuales
# ---------------------------------------------------------------------------

def score_keywords(combined: str) -> tuple[int, list[str]]:
    """
    Calcula el puntaje de palabras clave y retorna la lista de categorías
    temáticas detectadas.
    """
    total = 0
    seen_claves: set[str] = set()
    categorias: set[str] = set()

    for kw in config.KEYWORDS:
        clave_norm = _normalize(kw["clave"])
        if clave_norm in seen_claves:
            continue
        if clave_norm in combined:
            total += kw["puntaje"]
            seen_claves.add(clave_norm)
            categorias.add(kw["categoria"])

    return total, sorted(categorias)


def score_entity(combined: str) -> int:
    """Puntaje por entidad compradora prioritaria."""
    total = 0
    seen: set[str] = set()
    for ent in config.PRIORITY_ENTITIES:
        ent_norm = _normalize(ent["entidad"])
        if ent_norm in seen:
            continue
        if ent_norm in combined:
            total += ent["puntaje"]
            seen.add(ent_norm)
    return total


def score_territory(combined: str) -> int:
    """Puntaje por territorio prioritario."""
    total = 0
    seen: set[str] = set()
    for terr in config.PRIORITY_TERRITORIES:
        terr_norm = _normalize(terr["territorio"])
        if terr_norm in seen:
            continue
        if terr_norm in combined:
            total += terr["puntaje"]
            seen.add(terr_norm)
    return total


def score_discard(combined: str) -> int:
    """Penalización por palabras de descarte."""
    total = 0
    seen: set[str] = set()
    for dk in config.DISCARD_KEYWORDS:
        clave_norm = _normalize(dk["clave"])
        if clave_norm in seen:
            continue
        if clave_norm in combined:
            total += dk["penalizacion"]
            seen.add(clave_norm)
    return total


def score_vigencia(fecha_cierre: str | None) -> int:
    """
    Puntaje basado en los días que faltan para el cierre del proceso.
    Acepta fechas ISO 8601 o None.
    """
    if not fecha_cierre:
        return 0

    try:
        # SECOP puede devolver timestamps completos o solo fechas
        if "T" in fecha_cierre:
            cierre_dt = datetime.fromisoformat(fecha_cierre[:19])
            cierre = cierre_dt.date()
        else:
            cierre = date.fromisoformat(fecha_cierre[:10])
    except (ValueError, TypeError):
        return 0

    dias = (cierre - date.today()).days

    for rule in config.VIGENCIA_RULES:
        if dias <= rule["max_dias"]:
            return rule["puntaje"]
    return 0


def infer_publico(combined: str) -> str:
    """Infiere el público objetivo a partir del texto combinado."""
    checks = [
        ("asociación", "Asociaciones"),
        ("cooperativa", "Cooperativas"),
        ("fundación", "Fundaciones"),
        ("productor", "Productores"),
        ("campesino", "Campesinos"),
        ("pescador", "Pescadores"),
        ("piscicultor", "Piscicultores"),
        ("operador", "Operadores"),
    ]
    publicos = []
    for term, label in checks:
        if _normalize(term) in combined:
            publicos.append(label)
    return ", ".join(publicos) if publicos else "General"


def get_priority_label(total: int) -> str:
    """Devuelve la etiqueta de prioridad según el puntaje total."""
    if total >= config.THRESHOLD_ALTA:
        return config.PRIORIDAD_ALTA
    if total >= config.THRESHOLD_MEDIA:
        return config.PRIORIDAD_MEDIA
    if total >= config.THRESHOLD_BAJA:
        return config.PRIORIDAD_BAJA
    return config.PRIORIDAD_DESCARTAR


def get_aplica_label(priority: str) -> str:
    """Etiqueta de aplicabilidad para AGRODASIN."""
    mapping = {
        config.PRIORIDAD_ALTA: "SÍ – REVISAR YA",
        config.PRIORIDAD_MEDIA: "SÍ – REVISIÓN TÉCNICA",
        config.PRIORIDAD_BAJA: "SOLO INFORMATIVA",
        config.PRIORIDAD_DESCARTAR: "NO",
    }
    return mapping.get(priority, "NO")


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def score_record(record: dict[str, Any]) -> dict[str, Any]:
    """
    Enriquece un registro crudo de SECOP II con todos los campos de
    puntuación y clasificación de AGRODASIN.

    Devuelve el mismo dict con los campos adicionales añadidos.
    """
    combined = _combined_text(record)

    p_kw, categorias = score_keywords(combined)
    p_ent = score_entity(combined)
    p_terr = score_territory(combined)
    p_desc = score_discard(combined)
    p_vig = score_vigencia(record.get("fecha_limite_de_recepcion"))
    p_total = p_kw + p_ent + p_terr + p_desc + p_vig

    priority = get_priority_label(p_total)

    result = dict(record)
    result.update(
        {
            "puntaje_palabras_clave": p_kw,
            "puntaje_entidad": p_ent,
            "puntaje_territorio": p_terr,
            "penalizacion_descarte": p_desc,
            "puntaje_vigencia": p_vig,
            "puntaje_total": p_total,
            "nivel_prioridad": priority,
            "aplica_agrodasin": get_aplica_label(priority),
            "categorias_detectadas": categorias,
            "publico_objetivo": infer_publico(combined),
        }
    )
    return result


def score_records(records: list[dict]) -> list[dict]:
    """Aplica score_record a una lista de registros y ordena por puntaje."""
    scored = [score_record(r) for r in records]
    scored.sort(key=lambda r: r["puntaje_total"], reverse=True)
    return scored
