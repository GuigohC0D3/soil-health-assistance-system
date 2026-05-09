from unittest.mock import patch


class TestSimulateLiming:
    @patch("app.services.simulation_service.OpenAI")
    def test_valid_liming_request(self, mock_openai, client, test_analysis):
        mock_openai.return_value.chat.completions.create.return_value.choices[
            0
        ].message.content = "Narrativa de teste."

        response = client.post(
            "/api/simulate/liming",
            json={
                "analise_id": test_analysis.id,
                "dosagem_calcario": 2.0,
                "cultura": "Soja",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "antes" in data
        assert "depois" in data
        assert "narrativa" in data
        assert data["depois"]["v_pct_simulado"] >= data["antes"]["v_pct"]

    @patch("app.services.simulation_service.OpenAI")
    def test_zero_dosagem_no_change(self, mock_openai, client, test_analysis):
        mock_openai.return_value.chat.completions.create.return_value.choices[
            0
        ].message.content = "Narrativa."

        response = client.post(
            "/api/simulate/liming",
            json={
                "analise_id": test_analysis.id,
                "dosagem_calcario": 0.0,
                "cultura": "Soja",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["depois"]["v_pct_simulado"] == data["antes"]["v_pct"]

    def test_nonexistent_analysis_returns_404(self, client):
        response = client.post(
            "/api/simulate/liming",
            json={
                "analise_id": 99999,
                "dosagem_calcario": 2.0,
                "cultura": "Soja",
            },
        )
        assert response.status_code == 404

    def test_missing_cultura_returns_422(self, client, test_analysis):
        response = client.post(
            "/api/simulate/liming",
            json={
                "analise_id": test_analysis.id,
                "dosagem_calcario": 2.0,
            },
        )
        assert response.status_code == 422
