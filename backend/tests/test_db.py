from decimal import Decimal

from calculator import calcular_cotizacion
from db import guardar, limpiar_memoria, listar, obtener


def setup_function():
    limpiar_memoria()


def test_guardar_asigna_id_unico_y_se_puede_consultar():
    cotizacion = calcular_cotizacion("1000", "0", "0", "libros")
    guardada = guardar(cotizacion)
    leida = obtener(guardada["id"])

    assert guardada["id"]
    assert leida["cif"] == Decimal("1000.00")
    assert leida["dai"] == Decimal("0.00")


def test_dos_cotizaciones_tienen_id_distinto():
    primera = guardar(calcular_cotizacion("100", "0", "0", "ropa"))
    segunda = guardar(calcular_cotizacion("100", "0", "0", "ropa"))

    assert primera["id"] != segunda["id"]


def test_obtener_id_inexistente_devuelve_none():
    assert obtener("no-existe") is None


def test_listar_devuelve_solo_las_del_usuario():
    guardar({**calcular_cotizacion("100", "0", "0", "ropa"), "usuario": "admin"})
    guardar({**calcular_cotizacion("200", "0", "0", "libros"), "usuario": "otro"})

    propias = listar("admin")

    assert len(propias) == 1
    assert propias[0]["categoria"] == "6109.10.00.00"
