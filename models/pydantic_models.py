from pydantic import BaseModel

class ClienteCreate(BaseModel):
    nombre: str

class CategoriaCreate(BaseModel):
    nombre: str

class ClienteCategoriaRelation(BaseModel):
    id_cliente: int
    id_categoria: int

class CuentaCreate(BaseModel):
    id: int
    id_cliente: int