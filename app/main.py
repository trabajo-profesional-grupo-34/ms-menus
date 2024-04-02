from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "It's alive!"}


@app.get("/hello/{name}")
def hello_name(name: str = "World"):
    return {"message": f"Hello, {name}!"}
