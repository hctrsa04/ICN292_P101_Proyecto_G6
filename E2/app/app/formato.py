# Funciones de formato que usan varias pantallas


def pesos(monto):
    # 12000 -> "$12.000" (separador de miles chileno)
    return "$" + f"{monto:,}".replace(",", ".")
