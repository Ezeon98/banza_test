import pytest
import sys
import os
import requests
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.pydantic_models import CuentaCreate, MovimientoCreate
from main import app
from database import SessionLocal
from models.db_models import Movimiento

# Creamos un cliente de prueba usando TestClient
client = TestClient(app)

session = SessionLocal()


def test_get_movimiento_info_success():
    # Crea un movimiento de prueba
    movimiento_data = MovimientoCreate(tipo="ingreso", importe=500)
    response = client.post("/movimientos_post/", json=movimiento_data.model_dump())
    movimiento_id = response.json()["id"]

    # Envía la solicitud GET
    response = client.get(f"/movimiento/{movimiento_id}/info")

    # Valida la respuesta
    assert response.status_code == 200


def test_get_movimiento_info_not_found():
    # ID de movimiento inexistente
    movimiento_id = 1000

    # Envía la solicitud GET
    response = client.get(f"/movimiento/{movimiento_id}/info")

    # Valida el error de movimiento no encontrado
    assert response.status_code == 404
    assert response.json() == {"detail": "Movimiento no encontrado"}


def test_delete_movimiento_success():
    # Crea un movimiento de prueba
    movimiento_data = MovimientoCreate(tipo="ingreso", importe=500)
    response = client.post("/movimientos_post/", json=movimiento_data.model_dump())
    movimiento_id = int(response.json()["id"])
    # assert response.json() == "teasad"

    # Envía la solicitud DELETE
    response = client.delete(f"/movimiento/{movimiento_id}/")

    # Valida la respuesta
    assert response.json() == {"message": "Movimiento eliminado exitosamente"}
    assert response.status_code == 200


def test_delete_movimiento_not_found():
    # ID de movimiento inexistente
    movimiento_id = 1000

    # Envía la solicitud DELETE
    response = client.delete(f"/movimiento/{movimiento_id}/")

    # Valida el error de movimiento no encontrado
    assert response.status_code == 404
    assert response.json() == {"detail": "Movimiento no encontrado"}
