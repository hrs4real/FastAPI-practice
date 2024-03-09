from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from starlette import status
from ..database import Base
from ..main import app
from ..routers.auth import get_current_user, get_db
from ..models import Todos
from fastapi.testclient import TestClient
import pytest


SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db" # Creating new db for testing

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, autofield=False)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'ab', 'id': 1, 'user_role': 'admin'}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code",
        description="Need to learn",
        priority=5,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"title": "Learn to code",
                                "description": "Need to learn",
                                "priority": 5,
                                "complete": False,
                                "owner_id": 1}]
