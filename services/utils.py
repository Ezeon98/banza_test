def get_saldo_cuenta(lista_movimientos):
    saldo_acumulado = 0
    for movimiento in lista_movimientos:
        tipo = movimiento.tipo.lower()
        importe = movimiento.importe
        if tipo == "ingreso":
            saldo_acumulado += importe
        elif tipo == "egreso":
            saldo_acumulado -= importe
    return saldo_acumulado
