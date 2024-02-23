from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Cuenta, Cliente, Movimiento
from models.pydantic_models import CuentaCreate
from services.utils import get_saldo_cuenta
import requests

router = APIRouter(
    tags=["Cuenta"],
)


@router.post("/cuentas_post/")
async def create_cuenta(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    # Verificar si el cliente existe
    cliente_existente = db.query(Cliente).filter(Cliente.id == cuenta_data.id_cliente).first()
    if cliente_existente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Crear la nueva cuenta con el cliente correspondiente
    nueva_cuenta = Cuenta(**cuenta_data.model_dump())
    db.add(nueva_cuenta)
    db.commit()
    return {"message": "Cuenta creada exitosamente", "id": f"{nueva_cuenta.id}"}


@router.get("/cuenta/usd/{cuenta_id}")
async def get_total_usd(cuenta_id: int, db: Session = Depends(get_db)):
    cuenta_existente = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if cuenta_existente is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    movs_query = db.query(Movimiento).filter(Movimiento.id_cuenta == cuenta_id).all()
    saldo_cuenta = get_saldo_cuenta(movs_query)
    cotizacion = requests.get("https://dolarapi.com/v1/dolares/bolsa")
    if cotizacion.status_code == 200:
        total_usd = round(float(saldo_cuenta) / float(cotizacion.json()["compra"]), 2)
    else:
        raise HTTPException(status_code=404, detail="Error al obtener Cotizacion del Dolar")
    return {f"Saldo de Cuenta {cuenta_id} en USD": total_usd}
