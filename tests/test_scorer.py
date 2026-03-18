"""
Tests unitarios del motor de puntuación AGRODASIN (scorer.py).
"""

import sys
import os
import pytest
from datetime import date, timedelta

# Asegurar que el módulo sea importable desde la raíz del repositorio
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from radar_agrodasin import scorer, config


# ---------------------------------------------------------------------------
# Utilidades de texto (_normalize, _combined_text)
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_lower(self):
        assert scorer._normalize("EXTENSIÓN") == "extension"

    def test_removes_tildes(self):
        assert scorer._normalize("acuicultura") == "acuicultura"
        assert scorer._normalize("piscícola") == "piscicola"

    def test_combined_fields(self):
        rec = {
            "nombre_de_la_entidad": "ADR Nacional",
            "nombre_del_procedimiento": "Asistencia Técnica Rural",
            "descripcion_del_procedimiento": "",
            "departamento": "Bolívar",
            "ciudad": "Mompox",
            "modalidad_de_contratacion": "",
            "estado_del_procedimiento": "",
            "codigo_unspsc": "",
        }
        combined = scorer._combined_text(rec)
        assert "adr" in combined
        assert "asistencia tecnica" in combined
        assert "bolivar" in combined
        assert "mompox" in combined


# ---------------------------------------------------------------------------
# score_keywords
# ---------------------------------------------------------------------------

class TestScoreKeywords:
    def test_extension_agropecuaria(self):
        combined = scorer._normalize("extensión agropecuaria en zona rural")
        score, cats = scorer.score_keywords(combined)
        assert score == 30
        assert "Extensión agropecuaria" in cats

    def test_piscicultura(self):
        combined = scorer._normalize("proyecto piscícola con estanques y alevinos")
        score, cats = scorer.score_keywords(combined)
        assert score >= 50   # piscícola(30) + estanques(20) + alevinos(20)
        assert "Piscicultura" in cats

    def test_multiple_categories(self):
        combined = scorer._normalize(
            "asistencia técnica y capacitación en agricultura familiar"
        )
        score, cats = scorer.score_keywords(combined)
        assert "Extensión agropecuaria" in cats
        assert "Formación" in cats
        assert "Agricultura" in cats

    def test_no_match(self):
        combined = scorer._normalize("compra de papel bond para oficina")
        score, cats = scorer.score_keywords(combined)
        assert score == 0
        assert cats == []

    def test_no_double_counting(self):
        """La misma clave no debe sumarse dos veces aunque aparezca más de una vez."""
        combined = scorer._normalize("piscicultura piscicultura piscicultura")
        score, cats = scorer.score_keywords(combined)
        assert score == 30   # solo una vez


# ---------------------------------------------------------------------------
# score_entity
# ---------------------------------------------------------------------------

class TestScoreEntity:
    def test_adr(self):
        combined = scorer._normalize("Agencia de Desarrollo Rural ADR")
        score = scorer.score_entity(combined)
        assert score >= 20

    def test_sena(self):
        combined = scorer._normalize("SENA Regional Bolívar")
        score = scorer.score_entity(combined)
        assert score == 20

    def test_no_entity(self):
        combined = scorer._normalize("empresa privada S.A.S.")
        score = scorer.score_entity(combined)
        assert score == 0


# ---------------------------------------------------------------------------
# score_territory
# ---------------------------------------------------------------------------

class TestScoreTerritory:
    def test_bolivar(self):
        combined = scorer._normalize("departamento de Bolívar")
        score = scorer.score_territory(combined)
        assert score == 20

    def test_talaigua(self):
        combined = scorer._normalize("municipio de Talaigua Nuevo")
        score = scorer.score_territory(combined)
        assert score == 25

    def test_no_territory(self):
        combined = scorer._normalize("Cundinamarca Bogotá D.C.")
        score = scorer.score_territory(combined)
        assert score == 0


# ---------------------------------------------------------------------------
# score_discard
# ---------------------------------------------------------------------------

class TestScoreDiscard:
    def test_armamento_full_penalty(self):
        combined = scorer._normalize("compra de armamento para fuerzas militares")
        penalty = scorer.score_discard(combined)
        assert penalty == -100

    def test_no_discard(self):
        combined = scorer._normalize("asistencia técnica rural en Bolívar")
        penalty = scorer.score_discard(combined)
        assert penalty == 0

    def test_software_penalty(self):
        combined = scorer._normalize("adquisición de software especializado")
        penalty = scorer.score_discard(combined)
        assert penalty == -20


# ---------------------------------------------------------------------------
# score_vigencia
# ---------------------------------------------------------------------------

class TestScoreVigencia:
    def test_vencido(self):
        past = (date.today() - timedelta(days=5)).isoformat()
        assert scorer.score_vigencia(past) == -50

    def test_cierra_pronto(self):
        soon = (date.today() + timedelta(days=2)).isoformat()
        assert scorer.score_vigencia(soon) == 25

    def test_cierra_en_una_semana(self):
        week = (date.today() + timedelta(days=7)).isoformat()
        assert scorer.score_vigencia(week) == 20

    def test_cierra_en_tres_semanas(self):
        month = (date.today() + timedelta(days=21)).isoformat()
        assert scorer.score_vigencia(month) == 10

    def test_fecha_none(self):
        assert scorer.score_vigencia(None) == 0

    def test_fecha_invalida(self):
        assert scorer.score_vigencia("FECHA MALA") == 0

    def test_timestamp_completo(self):
        future = (date.today() + timedelta(days=7)).isoformat() + "T17:00:00"
        assert scorer.score_vigencia(future) == 20


# ---------------------------------------------------------------------------
# infer_publico
# ---------------------------------------------------------------------------

class TestInferPublico:
    def test_asociacion(self):
        combined = scorer._normalize("para asociaciones campesinas")
        result = scorer.infer_publico(combined)
        assert "Asociaciones" in result

    def test_cooperativa(self):
        combined = scorer._normalize("cooperativas pesqueras")
        result = scorer.infer_publico(combined)
        assert "Cooperativas" in result

    def test_general(self):
        combined = scorer._normalize("cualquier persona natural o jurídica")
        result = scorer.infer_publico(combined)
        assert result == "General"


# ---------------------------------------------------------------------------
# get_priority_label
# ---------------------------------------------------------------------------

class TestGetPriorityLabel:
    def test_alta(self):
        assert scorer.get_priority_label(80) == config.PRIORIDAD_ALTA

    def test_media(self):
        assert scorer.get_priority_label(55) == config.PRIORIDAD_MEDIA

    def test_baja(self):
        assert scorer.get_priority_label(30) == config.PRIORIDAD_BAJA

    def test_descartar(self):
        assert scorer.get_priority_label(5) == config.PRIORIDAD_DESCARTAR

    def test_exact_threshold_alta(self):
        assert scorer.get_priority_label(config.THRESHOLD_ALTA) == config.PRIORIDAD_ALTA

    def test_exact_threshold_media(self):
        assert scorer.get_priority_label(config.THRESHOLD_MEDIA) == config.PRIORIDAD_MEDIA


# ---------------------------------------------------------------------------
# score_record — integración
# ---------------------------------------------------------------------------

class TestScoreRecord:
    def _make_record(self, **kwargs) -> dict:
        base = {
            "id_del_portafolio": "TEST-001",
            "referencia_del_proceso": "TEST-REF-001",
            "nombre_de_la_entidad": "",
            "nit_entidad": "",
            "departamento": "",
            "ciudad": "",
            "nombre_del_procedimiento": "",
            "descripcion_del_procedimiento": "",
            "estado_del_procedimiento": "Publicado",
            "modalidad_de_contratacion": "",
            "valor_total_estimado": "100000",
            "fecha_de_publicacion_del": "2026-01-01T00:00:00",
            "fecha_limite_de_recepcion": None,
            "urlproceso": "https://secop.gov.co/test",
            "codigo_unspsc": "",
        }
        base.update(kwargs)
        return base

    def test_alta_prioridad_record(self):
        rec = self._make_record(
            nombre_de_la_entidad="ADR Regional Bolívar",
            nombre_del_procedimiento=(
                "Extensión agropecuaria y asistencia técnica para piscicultura "
                "y asociaciones campesinas en Mompox"
            ),
            departamento="Bolívar",
            ciudad="Mompox",
            fecha_limite_de_recepcion=(date.today() + timedelta(days=15)).isoformat(),
        )
        result = scorer.score_record(rec)
        assert result["nivel_prioridad"] == config.PRIORIDAD_ALTA
        assert result["puntaje_total"] >= 70
        assert len(result["categorias_detectadas"]) > 0
        assert "aplica_agrodasin" in result

    def test_descartar_record(self):
        rec = self._make_record(
            nombre_de_la_entidad="MinTIC",
            nombre_del_procedimiento="Adquisición de armamento y equipos de vigilancia armada",
            departamento="Bogotá D.C.",
        )
        result = scorer.score_record(rec)
        assert result["nivel_prioridad"] == config.PRIORIDAD_DESCARTAR

    def test_all_fields_present(self):
        rec = self._make_record(
            nombre_del_procedimiento="Capacitación en acuicultura en Magdalena",
            departamento="Magdalena",
        )
        result = scorer.score_record(rec)
        required_fields = [
            "puntaje_palabras_clave",
            "puntaje_entidad",
            "puntaje_territorio",
            "penalizacion_descarte",
            "puntaje_vigencia",
            "puntaje_total",
            "nivel_prioridad",
            "aplica_agrodasin",
            "categorias_detectadas",
            "publico_objetivo",
        ]
        for field in required_fields:
            assert field in result, f"Campo faltante: {field}"

    def test_score_records_sorted(self):
        records = [
            self._make_record(
                id_del_portafolio="LOW",
                nombre_del_procedimiento="Papel para impresoras",
            ),
            self._make_record(
                id_del_portafolio="HIGH",
                nombre_de_la_entidad="ADR Bolívar",
                nombre_del_procedimiento="Asistencia técnica y extensión agropecuaria",
                departamento="Bolívar",
            ),
        ]
        scored = scorer.score_records(records)
        assert scored[0]["puntaje_total"] >= scored[1]["puntaje_total"]
        assert scored[0]["id_del_portafolio"] == "HIGH"


# ---------------------------------------------------------------------------
# Tests del generador (smoke tests)
# ---------------------------------------------------------------------------

class TestGenerator:
    def test_generate_html_dry_run(self, tmp_path):
        from radar_agrodasin import generator
        from radar_agrodasin.__main__ import SAMPLE_RECORDS

        scored = scorer.score_records(SAMPLE_RECORDS)
        output = str(tmp_path / "test_output.html")
        generator.generate_html(scored, output_path=output)

        with open(output, encoding="utf-8") as f:
            content = f.read()

        assert "Radar AGRODASIN" in content
        assert "SECOP" in content
        assert "Alta prioridad" in content or "ALTA" in content

    def test_generate_html_empty(self, tmp_path):
        from radar_agrodasin import generator

        output = str(tmp_path / "empty.html")
        generator.generate_html([], output_path=output)

        with open(output, encoding="utf-8") as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "Radar AGRODASIN" in content


# ---------------------------------------------------------------------------
# Tests del CLI (__main__)
# ---------------------------------------------------------------------------

class TestCLI:
    def test_dry_run_generates_file(self, tmp_path):
        from radar_agrodasin.__main__ import main

        output = str(tmp_path / "output.html")
        ret = main(["--dry-run", "--output", output])
        assert ret == 0
        assert os.path.exists(output)
        with open(output, encoding="utf-8") as f:
            content = f.read()
        assert "<!DOCTYPE html>" in content

    def test_parse_args_defaults(self):
        from radar_agrodasin.__main__ import parse_args

        args = parse_args([])
        assert args.output == "index.html"
        assert args.days == 90
        assert args.max_records == 5000
        assert not args.dry_run
        assert not args.verbose

    def test_parse_args_custom(self):
        from radar_agrodasin.__main__ import parse_args

        args = parse_args(["--dry-run", "--days", "30", "--output", "out.html"])
        assert args.dry_run
        assert args.days == 30
        assert args.output == "out.html"
