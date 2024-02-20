from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Cliente, CategoriaCliente, Categoria
from models.pydantic_models import ClienteCreate, ClienteCategoriaRelation

router = APIRouter(
    tags=["User"],
)

@router.get("/clientes_get/")
def get_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Cliente).all()
    return {"clientes": clientes}

@router.post("/clientes/")
def create_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = Cliente(**cliente_data.dict())  # Convertir ClienteCreate a Cliente
    db.add(db_cliente)
    db.commit()
    return {"message": "Cliente creado exitosamente"}

@router.delete("/clientes/{cliente_id}/")
def delete_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
    return {"message": "Cliente eliminado exitosamente"}

@router.post("/categorias_clientes/", response_model=None)
def add_cliente_to_categoria(cliente_categoria_relation: ClienteCategoriaRelation, db: Session = Depends(get_db)):
    # Verificar si la relación ya existe
    existing_relation = db.query(CategoriaCliente).filter_by(
        id_categoria=cliente_categoria_relation.id_categoria,
        id_cliente=cliente_categoria_relation.id_cliente
    ).first()
    if existing_relation:
        raise HTTPException(status_code=400, detail="La relación ya existe")
    
    cliente_existente = db.query(Cliente).filter(Cliente.id == cliente_categoria_relation.id_cliente).first()
    if cliente_existente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    categoria_existente = db.query(Categoria).filter(Categoria.id == cliente_categoria_relation.id_categoria).first()
    if categoria_existente is None:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Agregar la relación a la tabla CategoriaCliente
    categoria_cliente= CategoriaCliente(**cliente_categoria_relation.dict())
    db.add(categoria_cliente)
    db.commit()

    return {"message": "Cliente agregado a la categoría exitosamente"}