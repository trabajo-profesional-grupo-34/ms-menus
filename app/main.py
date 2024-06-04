from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, distinct, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import JSONResponse
import json
import math


SQLALCHEMY_DATABASE_URL = "postgresql://tobia:12345678@localhost/dev"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base
Base = declarative_base()

EMOTION_TO_VALENCE_AROUSAL = {
    #valence, arousal, angle diff
    "happy": (0.866, 0.5, 30),
    "surprise": (0.0, 1, 60),
    "fear": (-0.5, 0.866, 30),
    "angry": (-0.866, 0.5, 30),
    "disgust": (-1.0, 0.0, 30),
    "sad": (-0.866, -0.5, 30),
    "neutral": (0.0, 0.0, 0)
}

VALENCE_AROUSAL_TO_EMOTION = {v: k for k, v in EMOTION_TO_VALENCE_AROUSAL.items()}

# Define the Menu model
class DbMenu(Base):
    __tablename__ = "menu"
    __table_args__ = {"schema": "taca"}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=False, index=True)
    categoria_id = Column(Integer, unique=False, index=True)
    descripcion = Column(String, unique=False, index=True)
    preparacion = Column(String, unique=False, index=True)
    ingredientes = Column(String, unique=False, index=True)
    foto = Column(String, unique=False, index=False)
    arousal_resultante = Column(Float, unique= False, index=True)
    valencia_resultante = Column(Float, unique= False, index=True)
    emocion_resultante = Column(String, unique= False, index=True)
    numero_experiencias = Column(Integer, unique= False, index=True)

class DbCategoria(Base):
    __tablename__ = "categoria"
    __table_args__ = {"schema": "taca"}

    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, unique=True, index=True)
    descripcion = Column(String, unique=True, index=False)

class DbExperiencia(Base):
    __tablename__ = "experiencia"
    __table_args__ = {"schema": "taca"}

    id = Column('id', Integer, primary_key=True)
    usuario_id = Column('usuario_id', Integer, unique=False, index=False)
    menu_id = Column('menu_id', Integer, unique=False, index=False)
    emocion = Column('emocion', String, unique=False, index=False)
    emocion_arousal = Column('emocion_arousal', Float, unique=False, index=False)
    emocion_valencia = Column('emocion_valencia', Float, unique=False, index=False)
    sam_valencia = Column('sam_valencia', Float, unique=False, index=False)
    sam_arousal = Column('sam_arousal', Float, unique=False, index=False)
    arousal_resultante = Column('arousal_resultante', Float, unique=False, index=False)
    valencia_resultante = Column('valencia_resultante', Float, unique=False, index=False)
    emocion_resultante = Column('emocion_resultante', String, unique=False, index=False)


class Menu(BaseModel):
    nombre: Optional[str]
    categoria_id: Optional[int]
    descripcion: Optional[str]
    preparacion: Optional[str]
    ingredientes: Optional[list]
    foto: Optional[str]
    arousal_resultante: Optional[float]
    valencia_resultante: Optional[float]
    emocion_resultante: Optional[str]
    numero_experiencias: Optional[int]

class ExistingMenu(Menu):
    id: int

class Experiencia(BaseModel):
    usuario_id: Optional[int]
    menu_id: Optional[int]
    emocion: Optional[dict]
    emocion_arousal: Optional[float]
    emocion_valencia: Optional[float]
    sam_valencia: Optional[float]
    sam_arousal: Optional[float]
    arousal_resultante: Optional[float]
    valencia_resultante: Optional[float]
    emocion_resultante: Optional[str]

class MenuListResponse(BaseModel):
    users: list[ExistingMenu]
    total: int
    page: int
    per_page: int

class Categoria(BaseModel):
    categoria: Optional[str]
    descripcion: Optional[str]

app = FastAPI()

def get_emocion_resultante(valence, arousal):
    for (v, a, diff), emotion in VALENCE_AROUSAL_TO_EMOTION.items():
        max_angle = calculate_angle(v, a)
        angle = calculate_angle(valence, arousal)
        if max_angle - diff < angle and angle <= max_angle:
            return emotion
        
    return 'unknow'


def calculate_angle(x, y):
    # Calculate the angle in radians
    angle_radians = math.atan2(y, x)
    
    # Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)
    
    return angle_degrees

def update_average(current_average, count, new_value):
    # Calculate the new average
    new_average = (current_average * count + new_value) / (count + 1)
    
    return new_average


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


@app.get("/")
def read_root():
    return {"message": "It's alive!"}


@app.get("/hello/{name}")
def hello_name(name: str = "World"):
    return {"message": f"Hello, {name}!"}


@app.get("/menus")
def get_menus(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1)
):
    # Create a new session
    db = SessionLocal()

    # Query the database for the user with the specified ID
    offset = (page - 1) * per_page
    menus_query = db.query(DbMenu).offset(offset).limit(per_page)
    menus = [
        ExistingMenu(
            id=m.id,
            nombre=m.nombre, 
            categoria_id=m.categoria_id, 
            descripcion=m.descripcion, 
            preparacion=m.preparacion, 
            ingredientes=m.ingredientes.split(','), 
            foto=m.foto,
            arousal_resultante=m.arousal_resultante,
            valencia_resultante=m.valencia_resultante,
            emocion_resultante=m.emocion_resultante,
            numero_experiencias=m.numero_experiencias
        ) for m in menus_query.all()
    ]
    total_menus = db.query(DbMenu).count()

    # Close the session
    db.close()

    return MenuListResponse(
        users=menus,
        total=total_menus,
        page=page,
        per_page=per_page
    )


@app.get("/menus/{id}")
def get_menu(id: int):
    # Create a new session
    db = SessionLocal()

    # Query the database for the user with the specified ID
    menu = db.query(DbMenu).filter(DbMenu.id == id).first()

    # Close the session
    db.close()

    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    return ExistingMenu(
        id=menu.id,
        nombre=menu.nombre,
        categoria_id= menu.categoria_id,
        descripcion= menu.descripcion,
        preparacion= menu.preparacion,
        ingredientes= menu.ingredientes.split(','),
        foto= menu.foto,
        arousal_resultante= menu.arousal_resultante,
        valencia_resultante= menu.valencia_resultante,
        emocion_resultante= menu.emocion_resultante,
        numero_experiencias= menu.numero_experiencias
    )


@app.post("/experiencia", status_code=201)
def create_experiencia(experiencia: Experiencia):
    # Create a new session
    db = SessionLocal()

    new_exp = DbExperiencia()
    # Create a new User object
    for field, value in experiencia.dict(exclude_unset=True).items():
        if field == "emocion":
            value = str(value)

        setattr(new_exp, field, value)

    if experiencia.emocion:
        new_exp.emocion_valencia, new_exp.emocion_arousal, _ = EMOTION_TO_VALENCE_AROUSAL[experiencia.emocion["dominant_emotion"]]

    new_exp.valencia_resultante = (new_exp.emocion_valencia + new_exp.sam_valencia) / 2
    new_exp.arousal_resultante = (new_exp.emocion_arousal + new_exp.sam_arousal) / 2

    new_exp.emocion_resultante = get_emocion_resultante(new_exp.valencia_resultante, new_exp.arousal_resultante)

    # Add the new user to the session
    db.add(new_exp)

    menu = db.query(DbMenu).filter(DbMenu.id == new_exp.menu_id).first()
    menu.valencia_resultante = update_average(menu.valencia_resultante, menu.numero_experiencias, new_exp.valencia_resultante)
    menu.arousal_resultante = update_average(menu.arousal_resultante, menu.numero_experiencias, new_exp.arousal_resultante)
    menu.emocion_resultante = get_emocion_resultante(menu.valencia_resultante, menu.arousal_resultante)
    menu.numero_experiencias = menu.numero_experiencias + 1


    # Commit the session to persist the changes to the database
    db.commit()

    # Refresh the new experience object and update the menu calification 
    db.refresh(new_exp)
    db.refresh(menu)

    # Close the session
    db.close()


    return {
        "id": new_exp.id,
        "usuario_id": new_exp.usuario_id,
        "menu_id": new_exp.menu_id,
        "emocion": json.loads(new_exp.emocion.replace("\'", "\"").replace("None", "null")),
        "emocion_arousal": new_exp.emocion_arousal,
        "emocion_valencia": new_exp.emocion_valencia,
        "sam_valencia": new_exp.sam_valencia,
        "sam_arousal": new_exp.sam_arousal,
        "arousal_resultante": new_exp.arousal_resultante,
        "valencia_resultante": new_exp.valencia_resultante,
        "emocion_resultante": new_exp.emocion_resultante
    }


@app.post("/menus", status_code=201)
def create_menu(menu: Menu):
    # Create a new session
    db = SessionLocal()

    new_menu = DbMenu()
    # Create a new User object
    for field, value in menu.dict(exclude_unset=True).items():
        if field == "ingredientes":
            value = ','.join(value)

        setattr(new_menu, field, value)

    new_menu.arousal_resultante = 0
    new_menu.valencia_resultante = 0
    new_menu.emocion_resultante = "neutral"
    new_menu.numero_experiencias = 0

    # Add the new user to the session
    db.add(new_menu)

    # Commit the session to persist the changes to the database
    db.commit()

    # Refresh the new user object to get the updated id
    db.refresh(new_menu)

    # Close the session
    db.close()

    return {
        "id": new_menu.id,
        "nombre": new_menu.nombre,
        "categoria_id": new_menu.categoria_id,
        "descripcion": new_menu.descripcion,
        "preparacion": new_menu.preparacion,
        "ingredientes": new_menu.ingredientes.split(','),
        "arousal_resultante": new_menu.arousal_resultante,
        "valencia_resultante": new_menu.valencia_resultante,
        "emocion_resultante": new_menu.emocion_resultante,
        "numero_experiencias": new_menu.numero_experiencias
    }


@app.delete("/menus/{id}", status_code=200)
def delete_menu(id: int):
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


@app.get("/menu_por_categorias", summary="Obtiene todos los platos de una categoria")
def get_categories(categoria2):
    # Create a new session
    db = SessionLocal()

    # Query the database for categorias
    menus = db.query(DbMenu).filter(DbMenu.categoria_id == categoria2).all()

    # Close the session
    db.close()

    list_menu = []
    
    for menu in menus :
        vals = {}
        vals['nombre']=menu.nombre
        vals['categoria']=menu.categoria_id 
        vals['descripcion']=menu.descripcion
        vals['preparacion']=menu.preparacion
        vals['ingredientes']=','.join(menu.ingredientes)
        vals['foto']=menu.foto
        vals['arousal_resultante']=menu.arousal_resultante
        vals['valencia_resultante']=menu.valencia_resultante
        vals['emocion_resultante']=menu.emocion_resultante
        vals['numero_experiencias']=menu.numero_experiencias
        list_menu.append(vals)
        
    return list_menu

@app.put("/menu/{id}")
def update_menu(id: int, menu_update: Menu):
    # Create a new session
    db = SessionLocal()

    # Query the database for categorias
    menu = db.query(DbMenu).filter(DbMenu.id == id).first()
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")

    for field, value in menu_update.dict(exclude_unset=True).items():
        if field == "ingredientes":
            value = ','.join(value)

        setattr(menu, field, value)

    db.commit()
    db.refresh(menu)

    # Close the session
    db.close()

    return {
        "id": menu.id,
        "nombre": menu.nombre,
        "categoria": menu.categoria_id,
        "descripcion": menu.descripcion,
        "preparacion": menu.preparacion,
        "ingredientes": menu.ingredientes.split(','),
        "arousal_resultante": menu.arousal_resultante,
        "valencia_resultante": menu.valencia_resultante,
        "emocion_resultante": menu.emocion_resultante,
        "numero_experiencias": menu.numero_experiencias
    }


@app.post("/crear_categorias", status_code=201, summary="Crea una nueva categoria")
def create_categorias(categoria: Categoria):
    # Create a new session
    db = SessionLocal()

    # Create a new User object
    new_categoria = DbCategoria(
        categoria=categoria.categoria, 
        descripcion=categoria.descripcion
    )

    # Add the new user to the session
    db.add(new_categoria)

    # Commit the session to persist the changes to the database
    db.commit()

    # Refresh the new user object to get the updated id
    db.refresh(new_categoria)

    # Close the session
    db.close()

    return {
        "categoria": new_categoria.categoria,
        "descripcion": new_categoria.descripcion,
        "id": new_categoria.id
    }

@app.get("/consultar_categorias", summary="Consulta todas las categorias")
def get_categories():
    # Create a new session
    db = SessionLocal()

    # Query the database for categorias
    categorias = db.query(DbCategoria).distinct().all()

    # Close the session
    db.close()

    print(categorias)

    return {
        "categorias": [{"id": c.id, "categoria": c.categoria} for c in categorias]
    }

@app.get("/experianca_por_usuario_categoria", summary="Devuelve las experiencias seguna la categoria y usuario enviado por parametro")
def get_experiencia(usuarioid, categoriaid):
    list_exp = []
    # Create a new session
    db = SessionLocal()
    Lista_platos_por_categoria = db.query(DbMenu).filter(DbMenu.categoria_id==categoriaid).all()
    # Close the session
    db.close()
    
    print (Lista_platos_por_categoria)

    for plato in Lista_platos_por_categoria:
        print(plato.nombre)
        # Create a new session
        db = SessionLocal()
        experiencias = db.query(DbExperiencia, DbMenu).join(DbMenu, DbExperiencia.menu_id==DbMenu.id).filter(DbExperiencia.usuario_id == usuarioid).filter(DbExperiencia.menu_id==plato.id).all()
        # Close the session
        db.close()
        #exp_resultante = DbExperiencia
        vals = {}
        count = 0
        valencia_res = 0
        arousal_res = 0
        for exp, menu in experiencias :
            valencia_res = valencia_res + exp.valencia_resultante
            arousal_res = arousal_res + exp.arousal_resultante
            count = count + 1

        vals = {
            "id": menu.id,
            "nombre": menu.nombre,
            "categoria": menu.categoria_id,
            "descripcion": menu.descripcion,
            "preparacion": menu.preparacion,
            "ingredientes": menu.ingredientes.split(','),
            "arousal_resultante": arousal_res / count,
            "valencia_resultante": valencia_res / count,
            "emocion_resultante": get_emocion_resultante(valencia_res, arousal_res),
            "numero_experiencias": count
        }
        list_exp.append(vals)
    
    
    return list_exp