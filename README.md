# ms-template

## Programs to install
Postgress: https://www.postgresql.org/download/ \\
Then execute the following steps in a terminal:
1. Access to postgress terminal: `sudo -u postgres psql`
2. Create a user and password: `CREATE USER username WITH PASSWORD 'pass';`
3. Create dev database: `CREATE DATABASE dev;`
4. Grant permissions: `GRANT ALL PRIVILEGES ON DATABASE dev TO username;`
5. Exit postgress terminal and execute in the terminal: `psql -U username -d dev -c "CREATE SCHEMA taca;"`
6. Create menus table using: `python3 ddl/create_table.py`

## Run project
Execute the following commands in the root path:

```
> pip install -r requirements.txt
> uvicorn app.main:app --reload
```

Execute linter

```
> autopep8 --in-place --recursive .
```