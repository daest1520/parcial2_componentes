from datetime import date

import pytest

from cliente.domain.modelos import Categoria, ErrorValidacion, Viaje
from cliente.domain.validaciones import validar_lugar, validar_viaje

VIAJE = Viaje("v1", "Europa", "Italia", date(2026, 6, 10), date(2026, 6, 20))
CATEGORIA = Categoria(1, "Histórico")


def test_viaje_valido():
    nombre, destino, inicio, fin = validar_viaje(" Europa ", "Italia", "2026-06-10", "2026-06-20")
    assert nombre == "Europa"
    assert inicio == date(2026, 6, 10)
    assert fin == date(2026, 6, 20)


@pytest.mark.parametrize("nombre, destino, inicio, fin", [
    ("", "Italia", "2026-06-10", "2026-06-20"),
    ("Europa", " ", "2026-06-10", "2026-06-20"),
    ("Europa", "Italia", "", "2026-06-20"),
    ("Europa", "Italia", "2026-06-10", ""),
])
def test_viaje_con_campos_vacios(nombre, destino, inicio, fin):
    with pytest.raises(ErrorValidacion):
        validar_viaje(nombre, destino, inicio, fin)


def test_viaje_con_fecha_mal_escrita():
    with pytest.raises(ErrorValidacion, match="AAAA-MM-DD"):
        validar_viaje("Europa", "Italia", "10/06/2026", "2026-06-20")


def test_fecha_inicio_posterior_a_fecha_fin():
    with pytest.raises(ErrorValidacion, match="posterior"):
        validar_viaje("Europa", "Italia", "2026-06-20", "2026-06-10")


def test_lugar_valido():
    datos = validar_lugar(VIAJE, "Coliseo", "Anfiteatro", "Roma", CATEGORIA, "2026-06-12")
    assert datos == ("Coliseo", "Anfiteatro", "Roma", 1, date(2026, 6, 12))


@pytest.mark.parametrize("nombre, descripcion, ciudad, fecha", [
    ("", "Anfiteatro", "Roma", "2026-06-12"),
    ("Coliseo", "", "Roma", "2026-06-12"),
    ("Coliseo", "Anfiteatro", "", "2026-06-12"),
    ("Coliseo", "Anfiteatro", "Roma", ""),
])
def test_lugar_con_campos_vacios(nombre, descripcion, ciudad, fecha):
    with pytest.raises(ErrorValidacion):
        validar_lugar(VIAJE, nombre, descripcion, ciudad, CATEGORIA, fecha)


def test_lugar_sin_categoria():
    with pytest.raises(ErrorValidacion, match="categoría"):
        validar_lugar(VIAJE, "Coliseo", "Anfiteatro", "Roma", None, "2026-06-12")


@pytest.mark.parametrize("fecha", ["2026-06-09", "2026-06-21"])
def test_lugar_fuera_del_viaje(fecha):
    with pytest.raises(ErrorValidacion, match="entre 10/06/2026 y 20/06/2026"):
        validar_lugar(VIAJE, "Coliseo", "Anfiteatro", "Roma", CATEGORIA, fecha)


@pytest.mark.parametrize("fecha", ["2026-06-10", "2026-06-20"])
def test_lugar_en_el_primer_y_ultimo_dia(fecha):
    validar_lugar(VIAJE, "Coliseo", "Anfiteatro", "Roma", CATEGORIA, fecha)
