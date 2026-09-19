from decimal import Decimal

import pytest

from calculator import calcular_cotizacion


def test_cif_es_fob_mas_flete_mas_seguro():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="100",
        seguro="50",
        categoria="tecnologia",
    )

    assert resultado["cif"] == Decimal("1150.00")


def test_dai_tecnologia_es_15_por_ciento_del_cif():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="100",
        seguro="50",
        categoria="tecnologia",
    )

    # CIF 1150.00 * 0.15 = 172.50 (SAC 8506.10.20.00 NMF 15%)
    assert resultado["dai"] == Decimal("172.50")
    assert resultado["categoria"] == "8506.10.20.00"


def test_iva_es_12_por_ciento_de_cif_mas_dai():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="100",
        seguro="50",
        categoria="tecnologia",
    )

    assert resultado["iva"] == Decimal("158.70")


def test_totales_de_tecnologia():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="100",
        seguro="50",
        categoria="tecnologia",
    )

    assert resultado["total_impuestos"] == Decimal("331.20")
    assert resultado["total"] == Decimal("1481.20")


def test_ropa_aplica_dai_real_del_arancel():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="0",
        seguro="0",
        categoria="ropa",
    )

    # 6109.10.00.00 NMF 15%
    assert resultado["cif"] == Decimal("1000.00")
    assert resultado["dai"] == Decimal("150.00")
    assert resultado["iva"] == Decimal("138.00")


def test_repuestos_aplica_dai_real_del_arancel():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="0",
        seguro="0",
        categoria="repuestos",
    )

    # 8708.21.00.00 NMF 10%
    assert resultado["dai"] == Decimal("100.00")
    assert resultado["iva"] == Decimal("132.00")


def test_libros_no_pagan_dai():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="0",
        seguro="0",
        categoria="libros",
    )

    # 4901.91.00.00 NMF 0%
    assert resultado["dai"] == Decimal("0.00")
    assert resultado["iva"] == Decimal("120.00")


def test_acepta_codigo_sac_directo():
    resultado = calcular_cotizacion(
        fob="1000",
        flete="0",
        seguro="0",
        categoria="8506.10.20.00",
    )

    assert resultado["dai"] == Decimal("150.00")
    assert resultado["categoria"] == "8506.10.20.00"


def test_rechaza_valores_negativos():
    with pytest.raises(ValueError, match="negativos"):
        calcular_cotizacion(
            fob="-1",
            flete="0",
            seguro="0",
            categoria="libros",
        )


def test_rechaza_codigo_invalido():
    with pytest.raises(ValueError, match="Codigo"):
        calcular_cotizacion(
            fob="100",
            flete="0",
            seguro="0",
            categoria="alimentos",
        )
