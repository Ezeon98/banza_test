from fastapi import FastAPI
from routes import cliente, categoria, cuenta, movimiento
from database import engine, Base

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"message": "Bienvenido al de Banza hecho por Ezequiel Romano"}


app.include_router(cliente.router)
app.include_router(categoria.router)
app.include_router(cuenta.router)
app.include_router(movimiento.router)
