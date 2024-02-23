import pytest
import sys
import os
import requests
from fastapi.testclient import TestClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.pydantic_models import CuentaCreate
from main import app
from database import SessionLocal
from models.db_models import Movimiento

# Creamos un cliente de prueba usando TestClient
client = TestClient(app)

session = SessionLocal()


def test_get_total_usd_success():
    # Crea una cuenta de prueba
    cuenta_data = CuentaCreate(id=3333, id_cliente=1)
    response = client.post("/cuentas_post/", json=cuenta_data.model_dump())
    cuenta_id = response.json()["id"]
    cotizacion = requests.get("https://dolarapi.com/v1/dolares/bolsa")

    saldo_test = 1500
    session.add(Movimiento(id_cuenta=3333, tipo="ingreso", importe=saldo_test))
    session.commit()
    session.close()

    total_usd_assert = round(float(saldo_test) / float(cotizacion.json()["compra"]), 2)

    # Envía la solicitud GET
    response = client.get(f"/cuenta/usd/{cuenta_id}")

    # Valida la respuesta
    assert response.json() == {f"Saldo de Cuenta {cuenta_id} en USD": total_usd_assert}
    assert response.status_code == 200


def test_get_total_usd_cuenta_not_found():
    # ID de cuenta inexistente
    cuenta_id = 10000

    # Envía la solicitud GET
    response = client.get(f"/cuenta/usd/{cuenta_id}")

    # Valida el error de cuenta no encontrada
    assert response.status_code == 404
    assert response.json() == {"detail": "Cuenta no encontrada"}
