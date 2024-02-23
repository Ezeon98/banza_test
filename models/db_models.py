from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime, func
from database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)


class CategoriaCliente(Base):
    __tablename__ = "categorias_clientes"

    id_categoria = Column(Integer, ForeignKey("categorias.id"), primary_key=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), primary_key=True)


class Cuenta(Base):
    __tablename__ = "cuenta"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"))


class Movimiento(Base):
    __tablename__ = "movimiento"
    id = Column(Integer, primary_key=True, index=True)
    id_cuenta = Column(Integer, ForeignKey("cuenta.id"))
    tipo = Column(String, index=True)
    importe = Column(Numeric(6, 2), index=True)
    fecha = Column(DateTime, index=True, default=func.now())
