from types import SimpleNamespace
from unittest.mock import patch

from app.services.recommendation_service import (
    _get_p_thresholds,
    _desvio_normalizado,
    calcular_metricas,
    SoilMetrics,
)
from app.services.simulation_service import simular_calagem


class TestGetPThresholds:
    def test_none_returns_arenosa(self):
        result = _get_p_thresholds(None)
        assert result["min"] == 10.0
        assert result["otimo"] == 20.0

    def test_below_150_returns_arenosa(self):
        result = _get_p_thresholds(100.0)
        assert result["min"] == 10.0

    def test_between_150_and_350_returns_media(self):
        result = _get_p_thresholds(200.0)
        assert result["min"] == 7.0

    def test_above_350_returns_argilosa(self):
        result = _get_p_thresholds(400.0)
        assert result["min"] == 4.0


class TestDesvioNormalizado:
    def test_below_min_positive_deviation(self):
        result = _desvio_normalizado(4.0, 5.5, 6.0, 6.5)
        assert result > 0

    def test_at_otimo_returns_zero(self):
        result = _desvio_normalizado(6.0, 5.5, 6.0, 6.5)
        assert result == 0.0

    def test_above_max_negative_deviation(self):
        result = _desvio_normalizado(7.0, 5.5, 6.0, 6.5)
        assert result < 0


class TestCalcularMetricas:
    def _make_analysis(self, **kwargs):
        defaults = {
            "ph": 5.2,
            "calcio": 1.5,
            "magnesio": 0.4,
            "potassio": 0.10,
            "materia_organica": 2.0,
            "fosforo": 8.0,
            "teor_argila": 200.0,
            "observacoes": None,
        }
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_soma_bases(self):
        a = self._make_analysis()
        m = calcular_metricas(a)
        expected = round(1.5 + 0.4 + 0.10, 3)
        assert m.soma_bases == expected

    def test_ctc_not_none_and_positive(self):
        a = self._make_analysis()
        m = calcular_metricas(a)
        assert m.ctc is not None
        assert m.ctc > 0

    def test_saturacao_bases_in_range(self):
        a = self._make_analysis()
        m = calcular_metricas(a)
        assert m.saturacao_bases is not None
        assert 0 < m.saturacao_bases < 100

    def test_necessidade_calagem_positive_for_low_v(self):
        a = self._make_analysis()
        m = calcular_metricas(a)
        assert m.necessidade_calagem is not None
        assert m.necessidade_calagem > 0

    def test_score_in_range(self):
        a = self._make_analysis()
        m = calcular_metricas(a)
        assert 0 <= m.score_saude <= 100

    def test_healthy_soil_no_calagem(self):
        a = self._make_analysis(
            ph=6.5,
            calcio=3.5,
            magnesio=1.0,
            potassio=0.25,
            fosforo=None,
            materia_organica=None,
        )
        m = calcular_metricas(a)
        assert m.necessidade_calagem is None


class TestSimularCalagem:
    @patch("app.services.simulation_service.OpenAI")
    def test_v2_calculation(self, mock_openai):
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value.choices[
            0
        ].message.content = "Narrativa de teste."

        m = SoilMetrics(
            soma_bases=8.0,
            h_al_estimado=12.0,
            ctc=20.0,
            saturacao_bases=40.0,
            necessidade_calagem=2.5,
            score_saude=55.0,
        )
        result = simular_calagem(m, 1.0, "Soja", None)

        expected_v2 = 40.0 + (1.0 * 10 * 0.80 * 100) / 20.0
        assert result["depois"]["v_pct_simulado"] == 80.0
        assert result["depois"]["ph_simulado"] == round(4.0 + 0.025 * 80.0, 1)

    @patch("app.services.simulation_service.OpenAI")
    def test_narrativa_present(self, mock_openai):
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value.choices[
            0
        ].message.content = "Narrativa de teste."

        m = SoilMetrics(
            ctc=20.0,
            saturacao_bases=40.0,
            necessidade_calagem=2.5,
            score_saude=55.0,
        )
        result = simular_calagem(m, 1.0, "Soja", None)
        assert result["narrativa"] == "Narrativa de teste."

    def test_empty_dict_when_ctc_none(self):
        m = SoilMetrics(
            ctc=None,
            saturacao_bases=40.0,
        )
        result = simular_calagem(m, 1.0, "Soja", None)
        assert result == {}
