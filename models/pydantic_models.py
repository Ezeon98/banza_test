from pydantic import BaseModel


class ClienteCreate(BaseModel):
    nombre: str


class ClienteUpdate(BaseModel):
    id: int
    nombre: str


class CategoriaCreate(BaseModel):
    nombre: str


class ClienteCategoriaRelation(BaseModel):
    id_cliente: int
    id_categoria: int


class CuentaCreate(BaseModel):
    id: int
    id_cliente: int


class MovimientoCreate(BaseModel):
    id_cuenta: int = 1
    tipo: str = "ingreso"
    importe: float
