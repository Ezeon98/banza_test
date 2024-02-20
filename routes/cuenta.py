from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Cuenta, Cliente
from models.pydantic_models import CuentaCreate

router = APIRouter(
    tags=["Cuenta"],
)

@router.post("/cuenta/")
def create_cuenta(cuenta_data: CuentaCreate, db: Session = Depends(get_db)):
    # Verificar si el cliente existe
    cliente_existente = db.query(Cliente).filter(Cliente.id == cuenta_data.id_cliente).first()
    if cliente_existente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Crear la nueva cuenta con el cliente correspondiente
    nueva_cuenta = Cuenta(**cuenta_data.dict())
    db.add(nueva_cuenta)
    db.commit()
    return {"message": "Cuenta creada exitosamente"}