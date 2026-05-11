import datetime

from app.models.recommendation import PriorityLevel, Recommendation
from app.models.soil_analysis import SoilAnalysis


class TestDashboardStats:
    def test_empty_user_returns_zeros(self, client):
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["properties"] == 0
        assert data["analyses"] == 0
        assert data["recommendations"] == 0
        assert data["critical"] == 0

    def test_counts_property(self, client, test_property):
        response = client.get("/api/dashboard/stats")
        data = response.json()
        assert data["properties"] == 1

    def test_counts_analysis(self, client, test_analysis):
        response = client.get("/api/dashboard/stats")
        data = response.json()
        assert data["analyses"] == 1

    def test_counts_recommendation(self, client, db, test_analysis):
        rec = Recommendation(
            tipo="Calagem",
            descricao="Aplicar calcário",
            prioridade=PriorityLevel.ALTA,
            analise_id=test_analysis.id,
        )
        db.add(rec)
        db.commit()

        response = client.get("/api/dashboard/stats")
        data = response.json()
        assert data["recommendations"] == 1
        assert data["critical"] == 1

    def test_critical_counts_only_alta_priority(self, client, db, test_analysis):
        db.add(Recommendation(
            tipo="pH baixo",
            descricao="Ajustar pH",
            prioridade=PriorityLevel.ALTA,
            analise_id=test_analysis.id,
        ))
        db.add(Recommendation(
            tipo="Matéria orgânica",
            descricao="Aumentar MO",
            prioridade=PriorityLevel.BAIXA,
            analise_id=test_analysis.id,
        ))
        db.commit()

        response = client.get("/api/dashboard/stats")
        data = response.json()
        assert data["recommendations"] == 2
        assert data["critical"] == 1


class TestDashboardTrends:
    def test_empty_user_returns_empty_trends(self, client):
        response = client.get("/api/dashboard/trends")
        assert response.status_code == 200
        data = response.json()
        assert data["top3_propriedades"] == []
        assert data["ph_trend"] == []
        assert data["ph_trend_prop_id"] is None

    def test_top3_contains_property_with_analysis(self, client, test_analysis, test_property):
        response = client.get("/api/dashboard/trends")
        data = response.json()
        assert len(data["top3_propriedades"]) == 1
        entry = data["top3_propriedades"][0]
        assert entry["propriedade_id"] == test_property.id
        assert "score" in entry
        assert "ultima_analise" in entry

    def test_ph_trend_contains_analysis_ph(self, client, test_analysis):
        response = client.get("/api/dashboard/trends")
        data = response.json()
        assert len(data["ph_trend"]) == 1
        assert data["ph_trend"][0]["ph"] == 5.2

    def test_ph_trend_id_amostra_present(self, client, test_analysis):
        response = client.get("/api/dashboard/trends")
        data = response.json()
        assert data["ph_trend"][0]["id_amostra"] == "AM-001"

    def test_top3_limited_to_three(self, client, db, test_user):
        from app.models.property import Property

        for i in range(4):
            prop = Property(
                nome=f"Fazenda {i}",
                area_hectares=50.0,
                proprietario_id=test_user.id,
            )
            db.add(prop)
            db.flush()
            a = SoilAnalysis(
                id_amostra=f"AM-{i:03d}",
                data_analise=datetime.date(2024, 1, i + 1),
                ph=5.0 + i * 0.3,
                calcio=1.5,
                magnesio=0.4,
                potassio=0.10,
                propriedade_id=prop.id,
            )
            db.add(a)
        db.commit()

        response = client.get("/api/dashboard/trends")
        data = response.json()
        assert len(data["top3_propriedades"]) <= 3

    def test_property_without_analysis_not_in_trends(self, client, test_property):
        response = client.get("/api/dashboard/trends")
        data = response.json()
        # property exists but has no analysis → should not appear in top3
        assert data["top3_propriedades"] == []

    def test_ph_trend_excludes_null_ph(self, client, db, test_property):
        a = SoilAnalysis(
            id_amostra="AM-NOPH",
            data_analise=datetime.date(2024, 5, 1),
            ph=None,
            calcio=2.0,
            magnesio=0.6,
            potassio=0.18,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/dashboard/trends")
        data = response.json()
        assert all(e["ph"] is not None for e in data["ph_trend"])
