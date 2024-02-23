from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Cliente, CategoriaCliente, Categoria, Cuenta, Movimiento
from models.pydantic_models import ClienteCreate, ClienteCategoriaRelation, ClienteUpdate
from services.utils import get_saldo_cuenta

router = APIRouter(
    tags=["User"],
)


@router.get("/clientes_get/")
async def get_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return {"clientes": clientes}


@router.post("/clientes_post/")
async def create_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente_data.model_dump())  # Convertir ClienteCreate a Cliente
    db.add(db_cliente)
    db.commit()
    return {"message": "Cliente creado exitosamente", "id": f"{db_cliente.id}"}


@router.put("/clientes/{cliente_id}")
async def update_cliente(cliente_update: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_update.id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente.nombre = cliente_update.nombre
    db.commit()

    return {"message": "Cliente actualizado exitosamente"}


@router.delete("/clientes/{cliente_id}/")
async def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado exitosamente"}


@router.post("/categorias_clientes/", response_model=None)
async def add_cliente_to_categoria(
    cliente_categoria_relation: ClienteCategoriaRelation, db: Session = Depends(get_db)
):
    # Verificar si la relación ya existe
    existing_relation = (
        db.query(CategoriaCliente)
        .filter_by(
            id_categoria=cliente_categoria_relation.id_categoria,
            id_cliente=cliente_categoria_relation.id_cliente,
        )
        .first()
    )
    if existing_relation:
        raise HTTPException(status_code=400, detail="La relación ya existe")

    cliente_existente = (
        db.query(Cliente).filter(Cliente.id == cliente_categoria_relation.id_cliente).first()
    )
    if cliente_existente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    categoria_existente = (
        db.query(Categoria).filter(Categoria.id == cliente_categoria_relation.id_categoria).first()
    )
    if categoria_existente is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Agregar la relación a la tabla CategoriaCliente
    categoria_cliente = CategoriaCliente(**cliente_categoria_relation.model_dump())
    db.add(categoria_cliente)
    db.commit()

    return {"message": "Cliente agregado a la categoría exitosamente"}


@router.get("/cliente/{cliente_id}/info")
async def get_cliente_info(cliente_id: int, db: Session = Depends(get_db)):
    # Obtener el cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    categoria_cliente_relation = db.query(CategoriaCliente).filter(
        CategoriaCliente.id_cliente == cliente_id
    )
    id_categorias = [relacion.id_categoria for relacion in categoria_cliente_relation]

    categoria_query = db.query(Categoria).filter(Categoria.id.in_(id_categorias)).all()
    cuenta_query = db.query(Cuenta).filter(Cuenta.id_cliente == cliente_id).all()

    list_categorias = [categoria.nombre for categoria in categoria_query]
    list_cuentas = [cuenta.id for cuenta in cuenta_query]

    return {"Cliente": cliente.nombre, "Categorias": list_categorias, "Cuentas": list_cuentas}


@router.get("/cliente/{cliente_id}/movimientos")
async def get_cliente_movimiento(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    cuenta_query = db.query(Cuenta).filter(Cuenta.id_cliente == cliente_id).all()
    list_cuentas = [cuenta.id for cuenta in cuenta_query]
    if len(list_cuentas) == 0:
        raise HTTPException(status_code=404, detail="El Cliente no posee Cuentas")

    cuentas_dict = {}
    for cuenta in list_cuentas:
        cuentas_dict[f"Cuenta {cuenta}"] = 0
        movs_query = db.query(Movimiento).filter(Movimiento.id_cuenta == cuenta).all()
        saldo_cuenta = get_saldo_cuenta(movs_query)
        cuentas_dict[f"Cuenta {cuenta}"] = saldo_cuenta

    return cuentas_dict
