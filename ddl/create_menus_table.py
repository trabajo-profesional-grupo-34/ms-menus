# Import necessary modules
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


# Define the SQLAlchemy connection URL
DATABASE_URL = "postgresql://postgres:pass@localhost/dev"

# Create an engine
engine = create_engine(DATABASE_URL)

# Create a MetaData object
metadata = MetaData()

# Define the menus table within the taca schema
menus = Table(
    'menus', metadata,
    Column('id', Integer, primary_key=True),
    Column('nombre', String, unique=False, index=True),
    Column('categoria', String, unique=False, index=True),
    Column('descripcion', String, unique=False, index=True),
    Column('praparacion', String, unique=False, index=True),
    Column('ingredientes', String, unique=False, index=True),
    Column('foto', String, unique=False, index=False),
    schema='taca'  # Specify the schema name here
)

categoria = Table(
    'categoria', metadata,
    Column('id', Integer, primary_key=True),
    Column('categoria', String, unique=True, index=True),
    Column('descripcion', String, unique=False, index=False),
    schema='taca'  # Specify the schema name here
)


# Create the schema and table in the database
if __name__ == "__main__":
    metadata.create_all(engine)
    print("Schema table 'menus' and 'categoria' created successfully.")
