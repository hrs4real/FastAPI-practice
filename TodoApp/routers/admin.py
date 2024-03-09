from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session  # Importing Session from sqlalchemy.orm module to work with database sessions.
from starlette import status
from starlette.exceptions import HTTPException
from ..models import Todos  # Importing the models module where the SQLAlchemy models are defined.
from ..database import SessionLocal  # Importing the SessionLocal from the database module.
from typing import Annotated  # Importing Annotated from typing module to provide type hints with additional metadata.
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


# Defining a function named get_db that returns a database session.
def get_db():
    db = SessionLocal()  # Creating a new database session using SessionLocal.
    try:
        yield db  # Yielding the session to be used in the dependent function.
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id)
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo_model.delete()
    db.commit()