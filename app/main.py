from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, distinct
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import JSONResponse


SQLALCHEMY_DATABASE_URL = "postgresql://alex:usurero24@localhost/dev"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base
Base = declarative_base()

# Define the Menu model


class DbMenu(Base):
    __tablename__ = "menus"
    __table_args__ = {"schema": "taca"}

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, unique=True, index=True)
    descripcion = Column(String, unique=True, index=True)
    praparacion = Column(String, unique=True, index=True)
    ingredientes = Column(String, unique=True, index=True)


class Menu(BaseModel):
    categoria: str
    descripcion: str
    praparacion: str
    ingredientes: list


app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.get("/")
def read_root():
    return {"message": "It's alive!"}


@app.get("/hello/{name}")
def hello_name(name: str = "World"):
    return {"message": f"Hello, {name}!"}


@app.get("/menus/{id}")
def get_user(id: int):
    # Create a new session
    db = SessionLocal()

    # Query the database for the user with the specified ID
    menu = db.query(DbMenu).filter(DbMenu.id == id).first()

    # Close the session
    db.close()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    return {
        "id": menu.id,
        "categoria": menu.categoria,
        "descripcion": menu.descripcion,
        "praparacion": menu.praparacion,
        "ingredientes": menu.ingredientes.split(',')
    }


@app.get("/categorias")
def get_categories():
    # Create a new session
    db = SessionLocal()

    # Query the database for categorias
    categorias = db.query(DbMenu.categoria).distinct().all()

    # Close the session
    db.close()

    return {
        "categorias": [c[0] for c in categorias]
    }


@app.post("/menus", status_code=201)
def create_user(menu: Menu):
    # Create a new session
    db = SessionLocal()

    # Create a new User object
    new_menu = DbMenu(
        categoria=menu.categoria, 
        descripcion=menu.descripcion,
        praparacion=menu.praparacion,
        ingredientes=','.join(menu.ingredientes)
    )

    # Add the new user to the session
    db.add(new_menu)

    # Commit the session to persist the changes to the database
    db.commit()

    # Refresh the new user object to get the updated id
    db.refresh(new_menu)

    # Close the session
    db.close()

    return {
        "categoria": new_menu.categoria,
        "descripcion": new_menu.descripcion,
        "praparacion": new_menu.praparacion,
        "ingredientes": new_menu.ingredientes.split(','),
        "id": new_menu.id
    }


@app.delete("/menus/{id}", status_code=200)
def delete_user(id: int):
    # Create a new session
    db = SessionLocal()

    # Retrieve the user object by ID
    menu = db.query(DbMenu).filter(DbMenu.id == id).first()

    # If user is not found, return None or raise an exception
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    # Delete the user object from the session
    db.delete(menu)

    # Commit the session to persist the changes to the database
    db.commit()

    # Close the session
    db.close()

    return {
        "message": "Menu deleted successfully"
    }
