import datetime
from unittest.mock import patch


MOCK_RECS = {
    "recomendacoes": [
        {
            "tipo": "Calagem",
            "descricao": "Aplicar 2 t/ha de calcário.",
            "prioridade": "alta",
        }
    ]
}


class TestListAnalyses:
    def test_empty_returns_list(self, client):
        response = client.get("/api/analyses/")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_analysis(self, client, test_analysis):
        response = client.get("/api/analyses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id_amostra"] == "AM-001"

    def test_filter_by_propriedade_id(self, client, test_analysis, test_property):
        response = client.get(f"/api/analyses/?propriedade_id={test_property.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_filter_nonexistent_propriedade_returns_empty(self, client, test_analysis):
        response = client.get("/api/analyses/?propriedade_id=99999")
        assert response.status_code == 200
        assert response.json() == []

    def test_pagination_skip(self, client, test_analysis):
        response = client.get("/api/analyses/?skip=10")
        assert response.status_code == 200
        assert response.json() == []

    def test_invalid_limit_returns_422(self, client):
        response = client.get("/api/analyses/?limit=0")
        assert response.status_code == 422


class TestGetAnalysis:
    def test_get_existing_analysis(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_analysis.id
        assert data["ph"] == 5.2

    def test_get_nonexistent_returns_404(self, client):
        response = client.get("/api/analyses/99999")
        assert response.status_code == 404

    def test_response_includes_recomendacoes_field(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}")
        assert "recomendacoes" in response.json()


class TestCreateAnalysis:
    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_create_returns_201(self, mock_recs, client, test_property):
        mock_recs.return_value = []
        response = client.post(
            "/api/analyses/",
            json={
                "id_amostra": "AM-002",
                "data_analise": "2024-03-01",
                "ph": 6.0,
                "calcio": 2.5,
                "magnesio": 0.8,
                "potassio": 0.18,
                "materia_organica": 3.0,
                "fosforo": 12.0,
                "teor_argila": 250.0,
                "propriedade_id": test_property.id,
            },
        )
        assert response.status_code == 201
        assert response.json()["id_amostra"] == "AM-002"

    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_create_with_invalid_property_returns_404(self, mock_recs, client):
        mock_recs.return_value = []
        response = client.post(
            "/api/analyses/",
            json={
                "id_amostra": "AM-003",
                "data_analise": "2024-03-01",
                "propriedade_id": 99999,
            },
        )
        assert response.status_code == 404

    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_create_minimal_fields(self, mock_recs, client, test_property):
        mock_recs.return_value = []
        response = client.post(
            "/api/analyses/",
            json={
                "id_amostra": "AM-MIN",
                "data_analise": "2024-06-01",
                "propriedade_id": test_property.id,
            },
        )
        assert response.status_code == 201
        assert response.json()["ph"] is None


class TestUpdateAnalysis:
    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_update_ph(self, mock_recs, client, test_analysis):
        mock_recs.return_value = []
        response = client.put(
            f"/api/analyses/{test_analysis.id}",
            json={"ph": 6.5},
        )
        assert response.status_code == 200
        assert response.json()["ph"] == 6.5

    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_update_nonexistent_returns_404(self, mock_recs, client):
        mock_recs.return_value = []
        response = client.put(
            "/api/analyses/99999",
            json={"ph": 6.5},
        )
        assert response.status_code == 404

    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_update_multiple_fields(self, mock_recs, client, test_analysis):
        mock_recs.return_value = []
        response = client.put(
            f"/api/analyses/{test_analysis.id}",
            json={"ph": 6.2, "materia_organica": 3.5, "fosforo": 15.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["materia_organica"] == 3.5
        assert data["fosforo"] == 15.0


class TestDeleteAnalysis:
    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_delete_returns_204(self, mock_recs, client, test_analysis):
        mock_recs.return_value = []
        response = client.delete(f"/api/analyses/{test_analysis.id}")
        assert response.status_code == 204

    def test_delete_nonexistent_returns_404(self, client):
        response = client.delete("/api/analyses/99999")
        assert response.status_code == 404

    @patch("app.routers.soil_analyses.gerar_recomendacoes")
    def test_deleted_analysis_not_retrievable(self, mock_recs, client, test_analysis):
        mock_recs.return_value = []
        client.delete(f"/api/analyses/{test_analysis.id}")
        response = client.get(f"/api/analyses/{test_analysis.id}")
        assert response.status_code == 404


class TestExportCSV:
    def test_export_returns_csv_content_type(self, client, test_analysis):
        response = client.get("/api/analyses/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    def test_export_has_header_row(self, client, test_analysis):
        response = client.get("/api/analyses/export")
        lines = response.text.strip().split("\n")
        assert "id_amostra" in lines[0]
        assert "ph" in lines[0]

    def test_export_contains_data_row(self, client, test_analysis):
        response = client.get("/api/analyses/export")
        lines = response.text.strip().split("\n")
        assert len(lines) == 2
        assert "AM-001" in lines[1]

    def test_export_empty_when_no_analyses(self, client):
        response = client.get("/api/analyses/export")
        assert response.status_code == 200
        lines = response.text.strip().split("\n")
        assert len(lines) == 1  # apenas cabeçalho

    def test_export_filter_by_propriedade_id(self, client, test_analysis, test_property):
        response = client.get(f"/api/analyses/export?propriedade_id={test_property.id}")
        assert response.status_code == 200
        lines = response.text.strip().split("\n")
        assert len(lines) == 2


class TestFertilizerPlan:
    def test_returns_plan_structure(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}/fertilizer-plan")
        assert response.status_code == 200
        data = response.json()
        assert "calagem" in data
        assert "fosfato" in data
        assert "potassio" in data
        assert "nitrogenio" in data

    def test_nonexistent_analysis_returns_404(self, client):
        response = client.get("/api/analyses/99999/fertilizer-plan")
        assert response.status_code == 404

    def test_low_phosphorus_gives_high_dose(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}/fertilizer-plan")
        data = response.json()
        # test_analysis has fosforo=8.0 (< 10), should be "deficiente"
        assert data["fosfato"]["categoria"] == "deficiente"
        assert data["fosfato"]["p2o5_kg_ha"] == 80

    def test_low_potassio_gives_high_dose(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}/fertilizer-plan")
        data = response.json()
        # test_analysis has potassio=0.10, borderline "deficiente"
        assert data["potassio"]["k2o_kg_ha"] == 60

    def test_calagem_nc_positive_for_low_v(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}/fertilizer-plan")
        data = response.json()
        # test_analysis has ph=5.2 → V% < 65, so NC > 0
        assert data["calagem"]["nc_t_ha"] > 0

    def test_area_hectares_used_in_total(self, client, test_analysis):
        response = client.get(f"/api/analyses/{test_analysis.id}/fertilizer-plan")
        data = response.json()
        assert data["area_hectares"] == 100.0
        # ss_total must equal ss_kg_ha * 100
        expected_ss_total = round(data["fosfato"]["superfosfato_simples_kg_ha"] * 100.0, 1)
        assert data["fosfato"]["superfosfato_simples_total_kg"] == expected_ss_total
