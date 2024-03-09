from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db' # Used with sqlite3
# SQLALCHEMY is an ORM which is used by fast api

# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:admin@localhost/TodoApplicationDatabase'
# 'pip install psycopg2-binary' for interacting with a PostgreSQL database

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})
# Database engine is used to start or initialize the database and connect with the program(SQLite3)

# engine = create_engine(SQLALCHEMY_DATABASE_URL) # for production dbms

# We have to create a session local which will hold the data till data in session local storage is cleared
SessionLocal = sessionmaker(autocommit=False, autofield=False, bind=engine)

# Creating object of our database
Base = declarative_base()