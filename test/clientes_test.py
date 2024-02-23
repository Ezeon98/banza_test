import pytest
import sys
import os
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.pydantic_models import ClienteCreate, ClienteUpdate, ClienteCategoriaRelation
from main import app
from database import SessionLocal
from models.db_models import Cliente, CategoriaCliente, Cuenta, Movimiento

# Creamos un cliente de prueba usando TestClient
client = TestClient(app)

session = SessionLocal()


def test_get_clientes():
    # Hacemos una solicitud GET al endpoint '/clientes_get/'
    response = client.get("/clientes_get/")

    # Verificamos que la solicitud haya sido exitosa (código de respuesta 200)
    assert response.status_code == 200

    # Verificamos que la respuesta contenga la lista de clientes
    assert "clientes" in response.json()

    # Verificamos que la lista de clientes no esté vacía
    assert len(response.json()["clientes"]) > 0


def test_update_cliente_not_found():
    # Envía una solicitud PUT al endpoint con un ID de cliente inexistente
    cliente_updated = ClienteUpdate(id=1000, nombre="Mariaaa")
    response = client.put(f"/clientes/{cliente_updated.id}", json=cliente_updated.model_dump())

    # Valida el código de respuesta de la solicitud
    assert response.status_code == 404

    # Verifica que la respuesta contenga el mensaje de error
    assert response.json() == {"detail": "Cliente no encontrado"}


def test_update_cliente_success():
    # Crea un cliente de prueba
    cliente_data = ClienteCreate(id=10, nombre="Juan Pérez")
    response = client.post("/clientes_post/", json=cliente_data.model_dump())
    cliente_id = response.json()["id"]

    # Prepara los datos de actualización
    cliente_updated = ClienteUpdate(id=cliente_id, nombre="Maria")

    # Envía la solicitud PUT
    response = client.put(f"/clientes/{cliente_id}", json=cliente_updated.model_dump())

    # Valida la respuesta
    assert response.status_code == 200
    assert response.json() == {"message": "Cliente actualizado exitosamente"}

    cliente_updated = session.query(Cliente).filter(Cliente.id == cliente_id).first()
    assert cliente_updated.nombre == "Maria"
    session.close()


def test_delete_cliente_success():
    # Crea un cliente de prueba
    cliente_data = ClienteCreate(nombre="Juan Pérez")
    response = client.post("/clientes_post/", json=cliente_data.model_dump())
    cliente_id = response.json()["id"]

    # Envía la solicitud DELETE
    response = client.delete(f"/clientes/{cliente_id}/")

    # Valida la respuesta
    assert response.status_code == 200
    assert response.json() == {"message": "Cliente eliminado exitosamente"}

    cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()
    assert cliente is None
    session.close()


def test_delete_cliente_not_found():
    # ID de cliente inexistente
    cliente_id = 1000

    # Envía la solicitud DELETE
    response = client.delete(f"/clientes/{cliente_id}/")

    # Valida el código de error
    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente no encontrado"}


def test_add_cliente_to_categoria_success():
    # Crea una relación de prueba
    cliente_categoria_relation = ClienteCategoriaRelation(id_categoria=1, id_cliente=2)

    # Envía la solicitud POST
    response = client.post("/categorias_clientes/", json=cliente_categoria_relation.model_dump())

    # Valida la respuesta
    assert response.status_code == 200
    assert response.json() == {"message": "Cliente agregado a la categoría exitosamente"}


def test_add_cliente_to_categoria_cliente_not_found():
    # Crea una relación de prueba con un ID de cliente inexistente
    cliente_categoria_relation = ClienteCategoriaRelation(id_categoria=1, id_cliente=1000)

    # Envía la solicitud POST
    response = client.post("/categorias_clientes/", json=cliente_categoria_relation.model_dump())

    # Valida el error de cliente no encontrado
    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente no encontrado"}


def test_add_cliente_to_categoria_relation_exists():
    # Crea una relación de prueba
    cliente_categoria_relation = ClienteCategoriaRelation(id_categoria=2, id_cliente=2)

    existing_relation = CategoriaCliente(id_categoria=2, id_cliente=2)
    session.add(existing_relation)
    session.commit()

    session.close()

    # Envía la solicitud POST
    response = client.post("/categorias_clientes/", json=cliente_categoria_relation.model_dump())

    # Valida el error de relación existente
    assert response.status_code == 400
    assert response.json() == {"detail": "La relación ya existe"}
    session.delete(existing_relation)


def test_add_cliente_to_categoria_categoria_not_found():
    # Crea una relación de prueba con un ID de categoría inexistente
    cliente_categoria_relation = ClienteCategoriaRelation(id_categoria=1000, id_cliente=2)

    # Envía la solicitud POST
    response = client.post("/categorias_clientes/", json=cliente_categoria_relation.model_dump())

    # Valida el error de categoría no encontrada
    assert response.status_code == 404
    assert response.json() == {"detail": "Categoría no encontrada"}


def test_get_cliente_movimiento_success():
    # Crea un cliente de prueba
    cliente_data = ClienteCreate(nombre="Juan Pérez")
    response = client.post("/clientes_post/", json=cliente_data.model_dump())
    cliente_id = response.json()["id"]

    # Crea una cuenta de prueba
    session.add(Cuenta(id=1000, id_cliente=cliente_id))
    session.commit()
    session.close()

    # Crea un movimiento de prueba
    session.add(Movimiento(id_cuenta=1000, tipo="ingreso", importe=500))
    session.commit()
    session.close()

    # Envía la solicitud GET
    response = client.get(f"/cliente/{cliente_id}/movimientos")

    # Valida la respuesta
    assert response.status_code == 200
    assert response.json() == {"Cuenta 1000": 500}


def test_get_cliente_movimiento_not_found():
    # ID de cliente inexistente
    cliente_id = 1000

    # Envía la solicitud GET
    response = client.get(f"/cliente/{cliente_id}/movimientos")

    # Valida el error de cliente no encontrado
    assert response.status_code == 404
    assert response.json() == {"detail": "Cliente no encontrado"}


def test_get_cliente_movimiento_no_cuentas():
    # Crea un cliente sin cuentas
    cliente_data = ClienteCreate(nombre="María Gómez")
    response = client.post("/clientes_post/", json=cliente_data.model_dump())
    cliente_id = response.json()["id"]

    # Envía la solicitud GET
    response = client.get(f"/cliente/{cliente_id}/movimientos")

    # Valida el error de no tener cuentas
    assert response.status_code == 404
    assert response.json() == {"detail": "El Cliente no posee Cuentas"}
