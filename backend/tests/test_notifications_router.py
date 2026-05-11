import datetime

from app.models.soil_analysis import SoilAnalysis


class TestGetNotifications:
    def test_no_properties_returns_empty(self, client):
        response = client.get("/api/notifications/")
        assert response.status_code == 200
        assert response.json() == []

    def test_property_without_analysis_triggers_sem_analise(self, client, test_property):
        response = client.get("/api/notifications/")
        data = response.json()
        tipos = [a["tipo"] for a in data]
        assert "sem_analise" in tipos

    def test_property_with_recent_analysis_no_sem_analise_alert(
        self, client, test_analysis
    ):
        # test_analysis is from 2024-01-15, which is older than 6 months from 2026-05-11
        # so we expect sem_analise_recente but NOT sem_analise
        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "sem_analise" not in tipos

    def test_old_analysis_triggers_sem_analise_recente(self, client, test_analysis):
        # test_analysis date is 2024-01-15, which is > 6 months old
        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "sem_analise_recente" in tipos

    def test_fresh_analysis_no_sem_analise_recente(self, client, db, test_property):
        fresh = SoilAnalysis(
            id_amostra="AM-FRESH",
            data_analise=datetime.date.today(),
            ph=6.0,
            calcio=2.5,
            magnesio=0.8,
            potassio=0.20,
            propriedade_id=test_property.id,
        )
        db.add(fresh)
        db.commit()

        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "sem_analise_recente" not in tipos
        assert "sem_analise" not in tipos

    def test_critical_ph_triggers_ph_critico(self, client, db, test_property):
        a = SoilAnalysis(
            id_amostra="AM-ACID",
            data_analise=datetime.date.today(),
            ph=4.5,
            calcio=1.0,
            magnesio=0.3,
            potassio=0.08,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "ph_critico" in tipos

    def test_normal_ph_no_ph_critico(self, client, db, test_property):
        a = SoilAnalysis(
            id_amostra="AM-OK",
            data_analise=datetime.date.today(),
            ph=6.2,
            calcio=3.0,
            magnesio=0.9,
            potassio=0.20,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "ph_critico" not in tipos

    def test_low_v_triggers_v_baixo(self, client, db, test_property):
        # Very low pH + low bases → V% < 40
        a = SoilAnalysis(
            id_amostra="AM-LOWV",
            data_analise=datetime.date.today(),
            ph=4.8,
            calcio=0.5,
            magnesio=0.1,
            potassio=0.05,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "v_baixo" in tipos

    def test_critical_score_triggers_score_critico(self, client, db, test_property):
        # Very degraded soil → score < 40
        a = SoilAnalysis(
            id_amostra="AM-CRIT",
            data_analise=datetime.date.today(),
            ph=4.0,
            calcio=0.3,
            magnesio=0.05,
            potassio=0.02,
            materia_organica=0.5,
            fosforo=1.0,
            teor_argila=100.0,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/notifications/")
        tipos = [a["tipo"] for a in response.json()]
        assert "score_critico" in tipos

    def test_alta_priority_sorted_first(self, client, db, test_property):
        # pH < 5.0 → should produce alta priority alerts
        a = SoilAnalysis(
            id_amostra="AM-SORT",
            data_analise=datetime.date.today(),
            ph=4.5,
            calcio=0.5,
            magnesio=0.1,
            potassio=0.05,
            propriedade_id=test_property.id,
        )
        db.add(a)
        db.commit()

        response = client.get("/api/notifications/")
        alerts = response.json()
        priorities = [a["prioridade"] for a in alerts]
        # all "alta" must come before "media"
        seen_media = False
        for p in priorities:
            if p == "media":
                seen_media = True
            if seen_media and p == "alta":
                assert False, "alta priority alert appeared after media"

    def test_alert_includes_required_fields(self, client, test_property):
        response = client.get("/api/notifications/")
        alerts = response.json()
        assert len(alerts) > 0
        for alert in alerts:
            assert "tipo" in alert
            assert "mensagem" in alert
            assert "prioridade" in alert
            assert "propriedade_id" in alert
            assert "propriedade_nome" in alert

    def test_alert_propriedade_nome_matches(self, client, test_property):
        response = client.get("/api/notifications/")
        alerts = response.json()
        assert all(a["propriedade_nome"] == "Fazenda Teste" for a in alerts)
