from decimal import Decimal, ROUND_HALF_UP

import aranceles

TASA_IVA = Decimal("0.12")
CENTAVO = Decimal("0.01")

# Atajos de demo (siguen existiendo para pruebas simples)
ATAJOS = {
    "tecnologia": "8506.10.20.00",  # DAI NMF 15%
    "ropa": "6109.10.00.00",  # DAI NMF 15%
    "repuestos": "8708.21.00.00",  # DAI NMF 10%
    "libros": "4901.91.00.00",  # DAI NMF 0%
}


def _a_dinero(valor):
    return Decimal(str(valor)).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def _resolver_arancel(codigo_o_atajo):
    clave = str(codigo_o_atajo or "").strip()
    codigo = ATAJOS.get(clave.lower(), clave)
    item = aranceles.obtener(codigo)
    if item is None:
        raise ValueError("Codigo arancelario no valido")
    return item


def calcular_cotizacion(fob, flete, seguro, categoria):
    """
    categoria acepta:
    - codigo SAC (ej. 8506.10.20.00)
    - atajo demo: tecnologia, ropa, repuestos, libros
    """
    item = _resolver_arancel(categoria)
    tasa = Decimal(str(item["dai_nmf"])) / Decimal("100")

    fob_d = _a_dinero(fob)
    flete_d = _a_dinero(flete)
    seguro_d = _a_dinero(seguro)

    if fob_d < 0 or flete_d < 0 or seguro_d < 0:
        raise ValueError("Los valores no pueden ser negativos")

    cif = _a_dinero(fob_d + flete_d + seguro_d)
    dai = _a_dinero(cif * tasa)
    iva = _a_dinero((cif + dai) * TASA_IVA)
    total_impuestos = _a_dinero(dai + iva)
    total = _a_dinero(cif + total_impuestos)

    return {
        "fob": fob_d,
        "flete": flete_d,
        "seguro": seguro_d,
        "categoria": item["codigo"],
        "descripcion": item["descripcion"],
        "tasa_dai": tasa,
        "cif": cif,
        "dai": dai,
        "iva": iva,
        "total_impuestos": total_impuestos,
        "total": total,
    }
