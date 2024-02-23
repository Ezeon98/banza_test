from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.db_models import Categoria
from models.pydantic_models import CategoriaCreate

router = APIRouter(
    tags=["Categoria"],
)


@router.get("/categorias/")
async def get_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return {"categorias": categorias}


@router.post("/categorias/")
async def create_categoria(categoria_data: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = Categoria(**categoria_data.model_dump())
    db.add(db_categoria)
    db.commit()
    return {"message": "Categoria creada exitosamente"}
