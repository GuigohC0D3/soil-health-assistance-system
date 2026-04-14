"""
Seed com dados fictícios para demonstração.
Executa: python seed_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date
from app.core.security import hash_password
from app.database import SessionLocal
from app.models import User, Property, SoilAnalysis, Recommendation
from app.models.user import UserRole
from app.services.recommendation_service import gerar_recomendacoes


def seed():
    db = SessionLocal()
    try:
        # Limpar dados existentes
        db.query(Recommendation).delete()
        db.query(SoilAnalysis).delete()
        db.query(Property).delete()
        db.query(User).delete()
        db.commit()

        # ── USUÁRIOS ────────────────────────────────────────────────────
        users_data = [
            {"nome": "João Batista Silva",      "email": "joao@teste.com",   "papel": UserRole.PRODUTOR},
            {"nome": "Maria Aparecida Souza",   "email": "maria@teste.com",  "papel": UserRole.PRODUTOR},
            {"nome": "Carlos Eduardo Lima",     "email": "carlos@teste.com", "papel": UserRole.PRODUTOR},
            {"nome": "Ana Paula Ferreira",      "email": "ana@teste.com",    "papel": UserRole.TECNICO},
            {"nome": "Roberto Mendes Costa",    "email": "roberto@teste.com","papel": UserRole.TECNICO},
        ]
        users = []
        for u in users_data:
            user = User(hashed_password=hash_password("senha123"), **u)
            db.add(user)
            users.append(user)
        db.flush()

        joao, maria, carlos, ana, roberto = users

        # ── PROPRIEDADES ─────────────────────────────────────────────────
        props_data = [
            # João — 3 propriedades
            {"nome": "Fazenda Boa Vista",        "area_hectares": 320.0, "localizacao": "Rod. BR-163, km 78",        "cidade": "Sorriso",        "estado": "MT", "proprietario_id": joao.id},
            {"nome": "Sítio São João",           "area_hectares":  45.5, "localizacao": "Estrada Municipal, km 12",  "cidade": "Lucas do Rio Verde","estado": "MT","proprietario_id": joao.id},
            {"nome": "Chácara Vale Verde",       "area_hectares":  18.0, "localizacao": "Zona Rural s/n",            "cidade": "Sinop",          "estado": "MT", "proprietario_id": joao.id},
            # Maria — 2 propriedades
            {"nome": "Fazenda Santa Luzia",      "area_hectares": 210.0, "localizacao": "Rod. GO-010, km 34",        "cidade": "Rio Verde",      "estado": "GO", "proprietario_id": maria.id},
            {"nome": "Sítio Recanto do Sol",     "area_hectares":  60.0, "localizacao": "Estrada do Café, km 5",     "cidade": "Jataí",          "estado": "GO", "proprietario_id": maria.id},
            # Carlos — 3 propriedades
            {"nome": "Fazenda Três Irmãos",      "area_hectares": 480.0, "localizacao": "Rod. BR-364, km 210",       "cidade": "Rondonópolis",   "estado": "MT", "proprietario_id": carlos.id},
            {"nome": "Fazenda Campo Alegre",     "area_hectares": 155.0, "localizacao": "Rod. MT-130, km 22",        "cidade": "Primavera do Leste","estado":"MT","proprietario_id": carlos.id},
            {"nome": "Sítio Bela Aurora",        "area_hectares":  30.0, "localizacao": "Linha Rural 4, lote 7",     "cidade": "Campo Verde",    "estado": "MT", "proprietario_id": carlos.id},
        ]
        props = []
        for p in props_data:
            prop = Property(**p)
            db.add(prop)
            props.append(prop)
        db.flush()

        boa_vista, sao_joao, vale_verde, santa_luzia, recanto_sol, tres_irmaos, campo_alegre, bela_aurora = props

        # ── ANÁLISES DE SOLO ─────────────────────────────────────────────
        analyses_data = [
            # Fazenda Boa Vista — evolução ao longo do tempo
            {"id_amostra": "BV-2023-001", "data_analise": date(2023, 3, 10), "ph": 4.6, "materia_organica": 1.4, "fosforo": 3.5,  "potassio": 0.07, "calcio": 1.2, "magnesio": 0.3, "observacoes": "Solo muito ácido, pastagem degradada. Compactação visível.", "propriedade_id": boa_vista.id},
            {"id_amostra": "BV-2023-002", "data_analise": date(2023, 9, 15), "ph": 5.2, "materia_organica": 1.8, "fosforo": 6.0,  "potassio": 0.10, "calcio": 1.8, "magnesio": 0.5, "observacoes": "Após primeira calagem. Melhora gradual observada.", "propriedade_id": boa_vista.id},
            {"id_amostra": "BV-2024-001", "data_analise": date(2024, 3, 20), "ph": 5.8, "materia_organica": 2.6, "fosforo": 12.0, "potassio": 0.18, "calcio": 2.8, "magnesio": 0.8, "observacoes": "Solo em recuperação. Plantio direto implantado.", "propriedade_id": boa_vista.id},
            {"id_amostra": "BV-2024-002", "data_analise": date(2024, 9, 5),  "ph": 6.1, "materia_organica": 3.0, "fosforo": 16.5, "potassio": 0.22, "calcio": 3.4, "magnesio": 1.0, "observacoes": "Excelente resposta ao manejo corretivo. Soja produtiva.", "propriedade_id": boa_vista.id},

            # Sítio São João — solo com deficiências pontuais
            {"id_amostra": "SJ-2024-001", "data_analise": date(2024, 2, 14), "ph": 6.0, "materia_organica": 2.2, "fosforo": 8.5,  "potassio": 0.12, "calcio": 2.5, "magnesio": 0.7, "observacoes": "Área de horta. Deficiência de fósforo e potássio.", "propriedade_id": sao_joao.id},
            {"id_amostra": "SJ-2024-002", "data_analise": date(2024, 8, 22), "ph": 6.2, "materia_organica": 2.8, "fosforo": 13.0, "potassio": 0.20, "calcio": 2.9, "magnesio": 0.9, "observacoes": "Após adubação corretiva. Produção de milho safrinha.", "propriedade_id": sao_joao.id},

            # Chácara Vale Verde — solo alcalino
            {"id_amostra": "VV-2024-001", "data_analise": date(2024, 5, 30), "ph": 7.8, "materia_organica": 2.1, "fosforo": 22.0, "potassio": 0.30, "calcio": 5.2, "magnesio": 1.4, "observacoes": "Solo com pH elevado. Provável excesso de calcário anterior.", "propriedade_id": vale_verde.id},

            # Fazenda Santa Luzia — solo degradado
            {"id_amostra": "SL-2023-001", "data_analise": date(2023, 6, 10), "ph": 4.9, "materia_organica": 1.6, "fosforo": 4.8,  "potassio": 0.08, "calcio": 1.4, "magnesio": 0.4, "observacoes": "Área de cerrado nativo recém incorporada. Solo muito pobre.", "propriedade_id": santa_luzia.id},
            {"id_amostra": "SL-2024-001", "data_analise": date(2024, 1, 25), "ph": 5.5, "materia_organica": 2.0, "fosforo": 9.0,  "potassio": 0.14, "calcio": 2.1, "magnesio": 0.6, "observacoes": "Após calagem e fosfatagem de base. Plantio de soja.", "propriedade_id": santa_luzia.id},
            {"id_amostra": "SL-2024-002", "data_analise": date(2024, 7, 18), "ph": 5.9, "materia_organica": 2.5, "fosforo": 14.5, "potassio": 0.21, "calcio": 3.0, "magnesio": 0.9, "observacoes": "Solo respondendo bem. Segunda safra de soja com bom rendimento.", "propriedade_id": santa_luzia.id},

            # Sítio Recanto do Sol — solo em boas condições
            {"id_amostra": "RS-2024-001", "data_analise": date(2024, 4, 8),  "ph": 6.3, "materia_organica": 3.8, "fosforo": 20.0, "potassio": 0.32, "calcio": 4.5, "magnesio": 1.3, "observacoes": "Solo bem manejado por anos. Café e citros em produção.", "propriedade_id": recanto_sol.id},
            {"id_amostra": "RS-2024-002", "data_analise": date(2024, 10, 2), "ph": 6.5, "materia_organica": 4.1, "fosforo": 24.0, "potassio": 0.38, "calcio": 4.8, "magnesio": 1.5, "observacoes": "Manutenção. Solo em condições ideais para cafeicultura.", "propriedade_id": recanto_sol.id},

            # Fazenda Três Irmãos — variação entre talhões
            {"id_amostra": "TI-2024-001", "data_analise": date(2024, 2, 28), "ph": 5.1, "materia_organica": 1.9, "fosforo": 5.5,  "potassio": 0.09, "calcio": 1.6, "magnesio": 0.4, "observacoes": "Talhão norte, solo com histórico de erosão.", "propriedade_id": tres_irmaos.id},
            {"id_amostra": "TI-2024-002", "data_analise": date(2024, 2, 28), "ph": 6.0, "materia_organica": 2.9, "fosforo": 15.0, "potassio": 0.24, "calcio": 3.2, "magnesio": 1.0, "observacoes": "Talhão sul, bem manejado. Soja irrigada.", "propriedade_id": tres_irmaos.id},
            {"id_amostra": "TI-2024-003", "data_analise": date(2024, 8, 14), "ph": 5.7, "materia_organica": 2.4, "fosforo": 11.0, "potassio": 0.17, "calcio": 2.6, "magnesio": 0.8, "observacoes": "Talhão central após reforma. Milho segunda safra.", "propriedade_id": tres_irmaos.id},

            # Fazenda Campo Alegre
            {"id_amostra": "CA-2024-001", "data_analise": date(2024, 3, 15), "ph": 5.4, "materia_organica": 2.1, "fosforo": 7.5,  "potassio": 0.13, "calcio": 2.0, "magnesio": 0.55,"observacoes": "Solo em transição para plantio direto.", "propriedade_id": campo_alegre.id},
            {"id_amostra": "CA-2024-002", "data_analise": date(2024, 9, 20), "ph": 5.9, "materia_organica": 2.6, "fosforo": 13.5, "potassio": 0.20, "calcio": 2.8, "magnesio": 0.85,"observacoes": "Após primeiro ano de PD. Boa evolução de MO.", "propriedade_id": campo_alegre.id},

            # Sítio Bela Aurora — solo jovem
            {"id_amostra": "BA-2024-001", "data_analise": date(2024, 6, 5),  "ph": 4.7, "materia_organica": 1.5, "fosforo": 4.0,  "potassio": 0.08, "calcio": 1.3, "magnesio": 0.35,"observacoes": "Área recém desmatada. Primeiro uso agrícola.", "propriedade_id": bela_aurora.id},
        ]

        for a_data in analyses_data:
            analysis = SoilAnalysis(**a_data)
            db.add(analysis)
            db.flush()
            for rec in gerar_recomendacoes(analysis):
                db.add(Recommendation(**rec, analise_id=analysis.id))

        db.commit()

        # Resumo
        total_users   = db.query(User).count()
        total_props   = db.query(Property).count()
        total_anal    = db.query(SoilAnalysis).count()
        total_recs    = db.query(Recommendation).count()

        print("\n✅  Seed concluído!")
        print(f"   Usuários:    {total_users}")
        print(f"   Propriedades:{total_props}")
        print(f"   Análises:    {total_anal}")
        print(f"   Recomendações:{total_recs}")
        print("\n   Credenciais (todos com senha: senha123):")
        print("   joao@teste.com    — Produtor")
        print("   maria@teste.com   — Produtor")
        print("   carlos@teste.com  — Produtor")
        print("   ana@teste.com     — Técnico")
        print("   roberto@teste.com — Técnico")

    except Exception as e:
        db.rollback()
        print(f"❌  Erro: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
