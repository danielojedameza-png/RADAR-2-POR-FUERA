"""
Punto de entrada del Radar AGRODASIN.

Uso:
    python -m radar_agrodasin [opciones]

Opciones:
    --output PATH       Archivo HTML de salida (default: index.html)
    --days N            Filtrar procesos de los últimos N días (default: 90)
    --max-records N     Máximo de registros a descargar (default: 5000)
    --dry-run           Usa datos de muestra; no llama a la API
    --verbose           Activa logging detallado

Ejemplo rápido (datos reales):
    python -m radar_agrodasin --days 60 --output index.html

Ejemplo prueba:
    python -m radar_agrodasin --dry-run --output /tmp/radar_test.html
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone

from .fetch import fetch_all, build_recent_filter
from .scorer import score_records
from .generator import generate_html

logger = logging.getLogger("radar_agrodasin")


# ---------------------------------------------------------------------------
# Datos de muestra para --dry-run / pruebas sin red
# ---------------------------------------------------------------------------
SAMPLE_RECORDS: list[dict] = [
    {
        "id_del_portafolio": "SAMPLE-001",
        "referencia_del_proceso": "ADR-2024-001",
        "nombre_de_la_entidad": "Agencia de Desarrollo Rural - ADR",
        "nit_entidad": "900123456",
        "departamento": "Bolívar",
        "ciudad": "Mompox",
        "nombre_del_procedimiento": (
            "Prestación de servicios de asistencia técnica y extensión agropecuaria "
            "para pequeños productores rurales de Mompox"
        ),
        "descripcion_del_procedimiento": (
            "Contratar operadores para brindar asistencia técnica, extensión "
            "agropecuaria y acompañamiento a asociaciones campesinas en el municipio "
            "de Mompox, incluyendo piscicultura y agricultura familiar."
        ),
        "estado_del_procedimiento": "Publicado",
        "modalidad_de_contratacion": "Concurso de méritos",
        "valor_total_estimado": "280000000",
        "fecha_de_publicacion_del": "2026-03-10T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-04-15T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE001"
        ),
        "codigo_unspsc": "70141600",
    },
    {
        "id_del_portafolio": "SAMPLE-002",
        "referencia_del_proceso": "SENA-REG8-2024-003",
        "nombre_de_la_entidad": "SENA Regional Bolívar",
        "nit_entidad": "899999001",
        "departamento": "Bolívar",
        "ciudad": "Cartagena",
        "nombre_del_procedimiento": (
            "Capacitación en piscicultura y acuicultura para productores del "
            "Caribe colombiano"
        ),
        "descripcion_del_procedimiento": (
            "Formación técnica a 200 piscicultores y productores acuícolas en "
            "manejo de estanques, alevinos y alimento balanceado en el Caribe."
        ),
        "estado_del_procedimiento": "En presentación de ofertas",
        "modalidad_de_contratacion": "Contratación directa",
        "valor_total_estimado": "95000000",
        "fecha_de_publicacion_del": "2026-03-12T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-03-25T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE002"
        ),
        "codigo_unspsc": "10190000",
    },
    {
        "id_del_portafolio": "SAMPLE-003",
        "referencia_del_proceso": "ALC-TALAIGUA-2024-007",
        "nombre_de_la_entidad": "Alcaldía Municipal de Talaigua Nuevo",
        "nit_entidad": "800123789",
        "departamento": "Bolívar",
        "ciudad": "Talaigua Nuevo",
        "nombre_del_procedimiento": (
            "Fortalecimiento organizacional de asociaciones campesinas y "
            "apoyo a mercados campesinos locales"
        ),
        "descripcion_del_procedimiento": (
            "Implementar un programa de fortalecimiento de asociaciones, "
            "economía popular y compras públicas locales con productores de "
            "agricultura familiar en Talaigua Nuevo."
        ),
        "estado_del_procedimiento": "Publicado",
        "modalidad_de_contratacion": "Selección abreviada",
        "valor_total_estimado": "150000000",
        "fecha_de_publicacion_del": "2026-03-15T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-04-20T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE003"
        ),
        "codigo_unspsc": "80141701",
    },
    {
        "id_del_portafolio": "SAMPLE-004",
        "referencia_del_proceso": "ICBF-CESAR-2024-012",
        "nombre_de_la_entidad": "ICBF Regional Cesar",
        "nit_entidad": "899999046",
        "departamento": "Cesar",
        "ciudad": "Valledupar",
        "nombre_del_procedimiento": (
            "Suministro de alimentos para el Programa de Alimentación Escolar (PAE) "
            "con énfasis en compra local y agricultura familiar"
        ),
        "descripcion_del_procedimiento": (
            "Adquisición de alimentos frescos y procesados para el PAE en Valledupar "
            "priorizando proveedores de agricultura familiar y productores locales."
        ),
        "estado_del_procedimiento": "Evaluación de ofertas",
        "modalidad_de_contratacion": "Licitación pública",
        "valor_total_estimado": "1200000000",
        "fecha_de_publicacion_del": "2026-02-28T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-03-22T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE004"
        ),
        "codigo_unspsc": "50000000",
    },
    {
        "id_del_portafolio": "SAMPLE-005",
        "referencia_del_proceso": "MIN-TIC-2024-99",
        "nombre_de_la_entidad": "Ministerio de Tecnologías de la Información",
        "nit_entidad": "830115395",
        "departamento": "Bogotá D.C.",
        "ciudad": "Bogotá",
        "nombre_del_procedimiento": (
            "Adquisición de software especializado para infraestructura de datos"
        ),
        "descripcion_del_procedimiento": (
            "Compra de licencias de software especializado para infraestructura "
            "de sistemas de información del MinTIC."
        ),
        "estado_del_procedimiento": "Publicado",
        "modalidad_de_contratacion": "Acuerdo marco",
        "valor_total_estimado": "500000000",
        "fecha_de_publicacion_del": "2026-03-01T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-04-01T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE005"
        ),
        "codigo_unspsc": "43232000",
    },
    {
        "id_del_portafolio": "SAMPLE-006",
        "referencia_del_proceso": "AUNAP-CARIBE-2024-005",
        "nombre_de_la_entidad": "AUNAP Dirección Regional Caribe",
        "nit_entidad": "900234567",
        "departamento": "Magdalena",
        "ciudad": "Santa Marta",
        "nombre_del_procedimiento": (
            "Apoyo técnico a comunidades de pesca artesanal y acuicultura en el "
            "Magdalena y el Caribe"
        ),
        "descripcion_del_procedimiento": (
            "Acompañamiento técnico a pescadores artesanales y piscicultores para "
            "mejorar la producción y fortalecer las cooperativas pesqueras."
        ),
        "estado_del_procedimiento": "Publicado",
        "modalidad_de_contratacion": "Concurso de méritos",
        "valor_total_estimado": "320000000",
        "fecha_de_publicacion_del": "2026-03-14T00:00:00.000",
        "fecha_limite_de_recepcion": "2026-04-30T17:00:00.000",
        "urlproceso": (
            "https://community.secop.gov.co/Public/Tendering/OpportunityDetail/"
            "Index?noticeUID=CO1.NTC.SAMPLE006"
        ),
        "codigo_unspsc": "10190100",
    },
]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Radar AGRODASIN — genera el portal de oportunidades del campo."
    )
    parser.add_argument(
        "--output",
        default="index.html",
        help="Ruta del archivo HTML a generar (default: index.html)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Filtrar procesos de los últimos N días (default: 90)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=5000,
        help="Máximo de registros a descargar (default: 5000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Usa datos de muestra; no llama a la API real",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Activa logging detallado",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    if args.dry_run:
        logger.info("Modo dry-run: usando %d registros de muestra.", len(SAMPLE_RECORDS))
        raw_records = SAMPLE_RECORDS
    else:
        logger.info("Consultando SECOP II (últimos %d días)…", args.days)
        extra_where = build_recent_filter(days=args.days)
        raw_records = fetch_all(
            max_records=args.max_records, extra_where=extra_where
        )
        logger.info("Descargados %d registros crudos.", len(raw_records))

    logger.info("Puntuando registros…")
    scored = score_records(raw_records)
    logger.info(
        "Registros puntuados: %d (Alta=%d, Media=%d, Baja=%d, Descartar=%d)",
        len(scored),
        sum(1 for r in scored if r["nivel_prioridad"] == "ALTA"),
        sum(1 for r in scored if r["nivel_prioridad"] == "MEDIA"),
        sum(1 for r in scored if r["nivel_prioridad"] == "BAJA"),
        sum(1 for r in scored if r["nivel_prioridad"] == "DESCARTAR"),
    )

    logger.info("Generando HTML en '%s'…", args.output)
    generate_html(scored, output_path=args.output)
    logger.info("✅ Portal generado: %s", os.path.abspath(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
