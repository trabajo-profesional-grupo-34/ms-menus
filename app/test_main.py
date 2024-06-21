from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "It's alive!"}


def test_menu_creation():
    data = {
        "categoria": "c1",
        "descripcion": "plato de prueba",
        "praparacion": "preparas el plato",
        "ingredientes": ["i1", "i2", "i3", "i4"]
    }
    response = client.post("/menus", json=data)
    assert response.status_code == 201
    for key in data.keys():
        assert response.json()[key] == data[key]


def test_get_menu():
    data = {
        "categoria": "c1",
        "descripcion": "plato de prueba",
        "praparacion": "preparas el plato",
        "ingredientes": ["i1", "i2", "i3","i4"]
    }
    menu = client.post("/menus", json=data)
    response = client.get(f"/menus/{menu.json()['id']}")
    assert response.status_code == 200
    for key in data.keys():
        assert response.json()[key] == data[key]


def test_get_menu_not_found():
    response = client.get(f"/menus/{0}")
    assert response.status_code == 404
    assert response.json() == {"message": "Menu not found"}


def test_delete_menu_then_not_found():
    menu = client.post("/menus", json={
        "categoria": "c1",
        "descripcion": "plato de prueba",
        "praparacion": "preparas el plato",
        "ingredientes": ["i1", "i2", "i3","i4"]
    })
    response = client.delete(f"/menus/{menu.json()['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Menu deleted successfully"}


def test_delete_menu_not_found():
    response = client.delete(f"/menus/{0}")
    assert response.status_code == 404
    assert response.json() == {"message": "Menu not found"}


def test_hello_name_with_alex():
    response = client.get("/hello/Alex")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Alex!"}