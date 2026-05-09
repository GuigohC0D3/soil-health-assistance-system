import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("LLM_API_BASE", "https://api.openai.com/v1")
os.environ.setdefault("LLM_API_KEY", "test-key")
os.environ.setdefault("LLM_MODEL", "gpt-4")

import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.core.deps import get_current_user
from app.main import app
from app.models.user import User
from app.models.property import Property
from app.models.soil_analysis import SoilAnalysis

engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _db_cleanup():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db):
    user = User(
        nome="Test User",
        email="test@test.com",
        hashed_password="hashed",
        papel="produtor",
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_property(db, test_user):
    prop = Property(
        nome="Fazenda Teste",
        area_hectares=100.0,
        proprietario_id=test_user.id,
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@pytest.fixture
def test_analysis(db, test_property):
    analysis = SoilAnalysis(
        id_amostra="AM-001",
        data_analise=datetime.date(2024, 1, 15),
        ph=5.2,
        materia_organica=2.0,
        fosforo=8.0,
        potassio=0.10,
        calcio=1.5,
        magnesio=0.4,
        teor_argila=200.0,
        propriedade_id=test_property.id,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@pytest.fixture
def client(db, test_user):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    def _override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
