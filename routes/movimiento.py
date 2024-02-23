from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Movimiento, Cuenta
from models.pydantic_models import MovimientoCreate
from services.utils import get_saldo_cuenta

router = APIRouter(
    tags=["Movimiento"],
)


@router.get("/movimiento/{mov_id}/info")
async def get_movimiento_info(mov_id: int, db: Session = Depends(get_db)):
    movimiento = db.query(Movimiento).filter(Movimiento.id == mov_id).first()
    if movimiento is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return {"movimiento": movimiento}


@router.post("/movimientos_post/")
async def create_movimiento(movimiento_data: MovimientoCreate, db: Session = Depends(get_db)):
    db_movimiento = Movimiento(**movimiento_data.model_dump())
    cuenta = db.query(Cuenta).filter(Cuenta.id == movimiento_data.id_cuenta).first()
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    if movimiento_data.tipo.lower() not in ["egreso", "ingreso"]:
        raise HTTPException(status_code=400, detail="Tipo de movimiento no valido")

    if movimiento_data.tipo.lower() == "egreso":
        movs_query = db.query(Movimiento).filter(Movimiento.id_cuenta == cuenta.id).all()
        saldo = get_saldo_cuenta(movs_query)
        print(saldo)
        if (float(saldo) - float(movimiento_data.importe)) < 0:
            raise HTTPException(
                status_code=404, detail="No se puede realizar el egreso. Falta Dinero"
            )

    db.add(db_movimiento)
    db.commit()
    return {"message": "Movimiento creado exitosamente", "id": f"{db_movimiento.id}"}


@router.delete("/movimiento/{mov_id}/")
async def delete_movimiento(mov_id: int, db: Session = Depends(get_db)):
    movimiento = db.query(Movimiento).filter(Movimiento.id == mov_id).first()
    if movimiento is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(movimiento)
    db.commit()
    return {"message": "Movimiento eliminado exitosamente"}
