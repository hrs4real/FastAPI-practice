from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session  # Importing Session from sqlalchemy.orm module to work with database sessions.
from starlette import status
from starlette.exceptions import HTTPException
from ..models import Todos  # Importing the models module where the SQLAlchemy models are defined.
from ..database import SessionLocal  # Importing the SessionLocal from the database module.
from typing import Annotated  # Importing Annotated from typing module to provide type hints with additional metadata.
from .auth import get_current_user

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)


# Defining a function named get_db that returns a database session.
def get_db():
    db = SessionLocal()  # Creating a new database session using SessionLocal.
    try:
        yield db  # Yielding the session to be used in the dependent function.
    finally:
        db.close()  # Closing the session after it's used.


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# Creating an alias (db_dependency) for the Depends dependency with type Session.
# This is used to provide dependency injection for database sessions.
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]    # Used for the user authorization


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')

    todo_model = (db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first())  # Creating a variable which will process the query
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    todo_model = Todos(**todo_request.dict(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id'))
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    todo_model.delete()
    db.commit()
