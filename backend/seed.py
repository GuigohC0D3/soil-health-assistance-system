"""
Script de seed para popular o banco com dados de exemplo.
Executar: python seed.py
"""
import sys
import os

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

        # Usuários
        produtor = User(
            nome="João da Silva",
            email="joao@exemplo.com",
            hashed_password=hash_password("senha123"),
            papel=UserRole.PRODUTOR,
        )
        tecnico = User(
            nome="Maria Engenheira",
            email="maria@exemplo.com",
            hashed_password=hash_password("senha123"),
            papel=UserRole.TECNICO,
        )
        db.add_all([produtor, tecnico])
        db.flush()

        # Propriedades
        fazenda_boa_vista = Property(
            nome="Fazenda Boa Vista",
            area_hectares=120.5,
            localizacao="Rodovia BR-364, km 45",
            cidade="Rondonópolis",
            estado="MT",
            proprietario_id=produtor.id,
        )
        sitio_esperanca = Property(
            nome="Sítio Esperança",
            area_hectares=35.0,
            localizacao="Estrada Municipal, km 12",
            cidade="Uberlândia",
            estado="MG",
            proprietario_id=produtor.id,
        )
        db.add_all([fazenda_boa_vista, sitio_esperanca])
        db.flush()

        # Análises de solo — Fazenda Boa Vista (solo com problemas)
        analise_1 = SoilAnalysis(
            id_amostra="AM-2024-001",
            data_analise=date(2024, 3, 15),
            ph=4.8,
            materia_organica=1.8,
            fosforo=4.2,
            potassio=0.09,
            calcio=1.5,
            magnesio=0.4,
            observacoes="Área de pastagem degradada. Solo compactado.",
            propriedade_id=fazenda_boa_vista.id,
        )
        db.add(analise_1)
        db.flush()
        for rec in gerar_recomendacoes(analise_1):
            db.add(Recommendation(**rec, analise_id=analise_1.id))

        # Análises de solo — Fazenda Boa Vista (solo em recuperação)
        analise_2 = SoilAnalysis(
            id_amostra="AM-2024-002",
            data_analise=date(2024, 9, 20),
            ph=5.8,
            materia_organica=2.9,
            fosforo=14.0,
            potassio=0.22,
            calcio=3.2,
            magnesio=0.9,
            observacoes="Após aplicação de calcário e adubação corretiva. Melhora significativa.",
            propriedade_id=fazenda_boa_vista.id,
        )
        db.add(analise_2)
        db.flush()
        for rec in gerar_recomendacoes(analise_2):
            db.add(Recommendation(**rec, analise_id=analise_2.id))

        # Análises de solo — Sítio Esperança (solo em boas condições)
        analise_3 = SoilAnalysis(
            id_amostra="AM-2025-001",
            data_analise=date(2025, 1, 10),
            ph=6.2,
            materia_organica=3.5,
            fosforo=18.5,
            potassio=0.28,
            calcio=4.1,
            magnesio=1.2,
            observacoes="Solo em excelentes condições. Cultivo de milho e soja.",
            propriedade_id=sitio_esperanca.id,
        )
        db.add(analise_3)
        db.flush()
        for rec in gerar_recomendacoes(analise_3):
            db.add(Recommendation(**rec, analise_id=analise_3.id))

        db.commit()
        print("✅ Seed concluído com sucesso!")
        print(f"   Usuários criados: joao@exemplo.com / maria@exemplo.com (senha: senha123)")
        print(f"   Propriedades: {fazenda_boa_vista.nome}, {sitio_esperanca.nome}")
        print(f"   Análises: 3 análises com recomendações geradas automaticamente")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro no seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
