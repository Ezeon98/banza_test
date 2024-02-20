from fastapi import FastAPI
from routes import cliente, categoria, cuenta
from database import engine, Base

app = FastAPI()

# Importar rutas desde otros archivos
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al de Banza hecho por Ezequiel Romano"}

app.include_router(cliente.router)
app.include_router(categoria.router)
app.include_router(cuenta.router)



