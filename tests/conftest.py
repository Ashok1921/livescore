import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv
from app.auth import create_access_token, hash_password
from app.models import User

from app.main import app
from app.database import Base, get_db

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    # Fresh tables before each test, dropped after — full isolation between tests
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    



@pytest.fixture(scope="function")
def auth_headers(db_session):
    """Seeds a test admin user into the test DB and returns a valid bearer token for them."""
    test_user = User(username="test_admin", hashed_password=hash_password("test_password"))
    db_session.add(test_user)
    db_session.commit()

    token = create_access_token({"sub": "test_admin"})
    return {"Authorization": f"Bearer {token}"}