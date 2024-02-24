# Banza Test

## Ejecucion

Creamos entorno virtual

    python -m venv venv

Activamos entorno virtual

    .\venv\Scripts\activate
  
Instalamos dependencias

    pip install -r requirements.txt
Iniciamos Proyecto

    uvicorn main:app --reload

Se deja base de datos "test_banza_er.db" donde se dejan 2 Clientes, donde el primero (id:1) tiene 2 categorias y 2 cuentas asociadas, sin saldo ambas.

Para correr los test:

    pytest test/clientes_test.py -W ignore::DeprecationWarning
    pytest test/cuentas_test.py -W ignore::DeprecationWarning    
    pytest test/movimientos_test.py -W ignore::DeprecationWarning

Cualquier duda comunicarse con mi mail ezeon3@gmail.com