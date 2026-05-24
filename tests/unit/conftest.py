import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base, get_db
from app.models.city import City
from app.main import app

TEST_DB_URL = "sqlite:///./test_airpulse.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    from app.models import city, air_quality, weather
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    c = TestClient(app, raise_server_exceptions=True)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_city(db):
    city = City(
        name="TestCity",
        country="Testland",
        latitude=52.0,
        longitude=21.0,
        iqair_city="TestCity",
        iqair_state="TestState",
        iqair_country="Testland",
    )
    db.add(city)
    db.commit()
    db.refresh(city)
    return city
