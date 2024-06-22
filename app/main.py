from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, distinct, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import JSONResponse
import json
import math


SQLALCHEMY_DATABASE_URL = "postgresql://alex:usurero24@localhost/dev"
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

VALENCE_AROUSAL_TO_TASTE = {
    "comun": (0, 360, 0, 0.25),
    "exquisito": (0, 45, 0.25, 1.5),
    "delicioso": (45, 90, 0.25, 1.5),
    "feo": (90, 135, 0.25, 1.5),
    "desagradable": (135, 180, 0.25, 1.5),
    "pasado": (180, 225, 0.25, 1.5),
    "insulso": (225, 270, 0.25, 1.5),
    "poco sabroso": (270, 315, 0.25, 1.5),
    "sabroso": (315, 360, 0.25, 1.5),
}

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
    emocion_menu = Column('emocion_menu', String, unique=False, index=False)
    arousal_menu = Column('arousal_menu', Float, unique=False, index=False)
    valencia_menu = Column('valencia_menu', Float, unique=False, index=False)
    emocion_plato = Column('emocion_plato', String, unique=False, index=False)
    arousal_plato = Column('arousal_plato', Float, unique=False, index=False)
    valencia_plato = Column('valencia_plato', Float, unique=False, index=False)
    sam_valencia = Column('sam_valencia', Float, unique=False, index=False)
    sam_arousal = Column('sam_arousal', Float, unique=False, index=False)
    arousal_resultante = Column('arousal_resultante', Float, unique=False, index=False)
    valencia_resultante = Column('valencia_resultante', Float, unique=False, index=False)
    emocion_resultante = Column('emocion_resultante', String, unique=False, index=False)
    reseña = Column('reseña', String, unique=False, index=False)
    api = Column('api', String, unique=False, index=False)


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
    emocion_menu: Optional[dict]
    arousal_menu: Optional[float]
    valencia_menu: Optional[float]
    emocion_plato: Optional[dict]
    arousal_plato: Optional[float]
    valencia_plato: Optional[float]
    sam_valencia: Optional[float]
    sam_arousal: Optional[float]
    reseña: Optional[str]
    api: Optional[str]

class MenuListResponse(BaseModel):
    menus: list[ExistingMenu]
    total: int
    page: int
    per_page: int

class Categoria(BaseModel):
    categoria: Optional[str]
    descripcion: Optional[str]

app = FastAPI()

def get_emocion_resultante(valence, arousal):
    if valence == 0 and arousal == 0:
        return "comun"

    angle = calculate_angle(valence, arousal)
    module = math.sqrt(valence * valence + arousal * arousal)
    for taste, (min_angle, max_angle, min_module, max_module) in VALENCE_AROUSAL_TO_TASTE.items():
        if min_module <= module and max_module > module:
            if min_angle <= angle and max_angle > angle:
                return taste
        
    return 'undefined'


def calculate_angle(x, y):
    # Calculate the angle in radians
    angle_radians = math.atan2(y, x)
    
    # Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)

    if angle_degrees < 0:
        angle_degrees += 360
    
    return angle_degrees

def update_average(current_average, count, new_value):
    # Calculate the new average
    if(current_average is None):
        current_average = 0
    new_average = (current_average * count + new_value) / (count + 1)
    
    return new_average

def calculate_valence_arousal(emocion_json):
    valence = emocion_json["happy"] * EMOTION_TO_VALENCE_AROUSAL["happy"][0] / 100
    arousal = emocion_json["happy"] * EMOTION_TO_VALENCE_AROUSAL["happy"][1] / 100
    del emocion_json["happy"]
    del emocion_json["surprise"]
    del emocion_json["neutral"]

    highest_emotion_negative = sorted(emocion_json.items(), key=lambda item: item[1], reverse=True)[0]
    valence_negative = highest_emotion_negative[1] * EMOTION_TO_VALENCE_AROUSAL[highest_emotion_negative[0]][0] / 100
    return valence - valence_negative, arousal


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
        menus=menus,
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
        if field == "emocion_menu" or field == "emocion_plato":
            value = str(value)

        setattr(new_exp, field, value)

    if experiencia.api == 'deepface':
        new_exp.valencia_menu, new_exp.arousal_menu = calculate_valence_arousal(experiencia.emocion_menu["emotion"])
        new_exp.valencia_plato, new_exp.arousal_plato = calculate_valence_arousal(experiencia.emocion_plato["emotion"])

    new_exp.valencia_resultante = (new_exp.valencia_menu + new_exp.valencia_plato + new_exp.sam_valencia) / 3
    new_exp.arousal_resultante = (new_exp.arousal_menu + new_exp.arousal_plato + new_exp.sam_arousal) / 3

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
        "emocion_menu": json.loads(new_exp.emocion_menu.replace("\'", "\"").replace("None", "null")),
        "arousal_menu": new_exp.arousal_menu,
        "valencia_menu": new_exp.valencia_menu,
        "emocion_plato": json.loads(new_exp.emocion_plato.replace("\'", "\"").replace("None", "null")),
        "arousal_plato": new_exp.arousal_plato,
        "valencia_plato": new_exp.valencia_plato,
        "sam_valencia": new_exp.sam_valencia,
        "sam_arousal": new_exp.sam_arousal,
        "arousal_resultante": new_exp.arousal_resultante,
        "valencia_resultante": new_exp.valencia_resultante,
        "emocion_resultante": new_exp.emocion_resultante,
        "reseña": new_exp.reseña,
        "api": new_exp.api
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
    new_menu.emocion_resultante = "comun"
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
        "categoria_id": menu.categoria_id,
        "descripcion": menu.descripcion,
        "preparacion": menu.preparacion,
        "ingredientes": menu.ingredientes.split(','),
        "arousal_resultante": menu.arousal_resultante,
        "valencia_resultante": menu.valencia_resultante,
        "emocion_resultante": menu.emocion_resultante,
        "numero_experiencias": menu.numero_experiencias,
        "foto": menu.foto
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

    return {
        "categorias": [{"id": c.id, "categoria": c.categoria} for c in categorias]
    }

@app.get("/menu_por_usuario_categoria", summary="Devuelve las experiencias seguna la categoria y usuario enviado por parametro")
def get_experiencia(usuarioid: int, categoriaid: int):
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
        vals = {}
        count = 0
        valencia_res = 0
        arousal_res = 0
        for exp, menu in experiencias :
            valencia_res = valencia_res + exp.valencia_resultante
            arousal_res = arousal_res + exp.arousal_resultante
            count = count + 1

        if count > 0:
            vals = {
                "id": plato.id,
                "nombre": plato.nombre,
                "categoria": plato.categoria_id,
                "descripcion": plato.descripcion,
                "preparacion": plato.preparacion,
                "ingredientes": plato.ingredientes.split(','),
                "arousal_resultante": arousal_res / count,
                "valencia_resultante": valencia_res / count,
                "emocion_resultante": get_emocion_resultante(valencia_res, arousal_res),
                "numero_experiencias": count
            }
            list_exp.append(vals)
    
    return list_exp