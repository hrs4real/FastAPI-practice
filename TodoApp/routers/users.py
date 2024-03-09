from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session  # Importing Session from sqlalchemy.orm module to work with database sessions.
from starlette import status
from starlette.exceptions import HTTPException
from ..models import Users  # Importing the models module where the SQLAlchemy models are defined.
from ..database import SessionLocal  # Importing the SessionLocal from the database module.
from typing import Annotated  # Importing Annotated from typing module to provide type hints with additional metadata.
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    prefix='/user',
    tags=['user']
)


# Defining a function named get_db that returns a database session.
def get_db():
    db = SessionLocal()  # Creating a new database session using SessionLocal.
    try:
        yield db  # Yielding the session to be used in the dependent function.
    finally:
        db.close()  # Closing the session after it's used.


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]    # Used for the user authorization
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=2)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
