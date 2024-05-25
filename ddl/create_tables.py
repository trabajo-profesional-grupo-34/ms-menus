# Import necessary modules
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float


# Define the SQLAlchemy connection URL
DATABASE_URL = "postgresql://alex:usurero24@localhost/dev"

# Create an engine
engine = create_engine(DATABASE_URL)

# Create a MetaData object
metadata = MetaData()

# Define the menus table within the taca schema
menu = Table(
    'menu', metadata,
    Column('id', Integer, primary_key=True),
    Column('nombre', String, unique=False, index=True),
    Column('categoria_id', String, unique=False, index=True),
    Column('descripcion', String, unique=False, index=True),
    Column('preparacion', String, unique=False, index=True),
    Column('ingredientes', String, unique=False, index=True),
    Column('foto', String, unique=False, index=False),
    Column('arousal_resultante', Float, unique=False, index=False),
    Column('valencia_resultante', Float, unique=False, index=False),
    Column('emocion_resultante', String, unique=False, index=False),
    Column('numero_experiencias', Integer, unique=False, index=False),
    schema='taca'  # Specify the schema name here
)

categoria = Table(
    'categoria', metadata,
    Column('id', Integer, primary_key=True),
    Column('categoria', String, unique=True, index=True),
    Column('descripcion', String, unique=False, index=False),
    schema='taca'  # Specify the schema name here
)

experiencia = Table(
    'experiencia', metadata,
    Column('id', Integer, primary_key=True),
    Column('usuario_id', Integer, unique=False, index=False),
    Column('menu_id', Integer, unique=False, index=False),
    Column('emocion', String, unique=False, index=False),
    Column('emocion_arousal', Float, unique=False, index=False),
    Column('emocion_valencia', Float, unique=False, index=False),
    Column('sam_valencia', Float, unique=False, index=False),
    Column('sam_arousal', Float, unique=False, index=False),
    Column('arousal_resultante', Float, unique=False, index=False),
    Column('valencia_resultante', Float, unique=False, index=False),
    Column('emocion_resultante', String, unique=False, index=False),
    schema='taca'  # Specify the schema name here
)


# Create the schema and table in the database
if __name__ == "__main__":
    metadata.create_all(engine)
    print("Schema table 'menus' and 'categoria' created successfully.")
