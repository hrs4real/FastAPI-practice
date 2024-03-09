from fastapi import FastAPI
from .models import Base
from .routers import auth, todos, admin, users
from .database import engine  # Importing the engine from the database module.

app = FastAPI()

Base.metadata.create_all(bind=engine)  # Creating the database tables defined in the models using the engine.

'''
@app.get('/healthy')
def health_check():
    return {'status': 'Healthy'}
'''

app.include_router(auth.router)  # Include the routers/auth.py file in the main file
app.include_router(todos.router)  # Include the routers/todos.py file in the main file
app.include_router(admin.router)
app.include_router(users.router)