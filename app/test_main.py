from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "It's alive!"}

def test_hello_name_with_world():
    response = client.get("/hello/World")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_hello_name_with_alex():
    response = client.get("/hello/Alex")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alex!"}
