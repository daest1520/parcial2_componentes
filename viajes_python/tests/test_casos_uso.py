import pytest

from cliente.domain.casos_uso import AgregarLugar, CrearViaje, ObtenerDetalleViaje, ObtenerViajes
from cliente.domain.modelos import ErrorValidacion
from tests.falsos import CATEGORIAS, RepositorioFalso


def test_viaje_creado_aparece_en_la_lista():
    repositorio = RepositorioFalso()
    CrearViaje(repositorio)("Europa", "Italia", "2026-06-10", "2026-06-20")
    viajes = ObtenerViajes(repositorio)()
    assert [(v.nombre, v.destino) for v in viajes] == [("Europa", "Italia")]


def test_viaje_invalido_no_se_guarda():
    repositorio = RepositorioFalso()
    with pytest.raises(ErrorValidacion):
        CrearViaje(repositorio)("Europa", "Italia", "2026-06-20", "2026-06-10")
    assert repositorio.viajes == []


def test_lugar_se_guarda_con_su_viaje_y_categoria():
    repositorio = RepositorioFalso()
    viaje = repositorio.agregar_viaje()
    AgregarLugar(repositorio)(viaje, "Coliseo", "Anfiteatro", "Roma", CATEGORIAS[1], "2026-06-12")
    assert repositorio.lugares[0].viaje_id == viaje.id
    assert repositorio.lugares[0].categoria.id == 2


def test_lugar_fuera_del_viaje_no_se_guarda():
    repositorio = RepositorioFalso()
    viaje = repositorio.agregar_viaje()
    with pytest.raises(ErrorValidacion):
        AgregarLugar(repositorio)(viaje, "Coliseo", "Anfiteatro", "Roma", CATEGORIAS[0], "2026-07-01")
    assert repositorio.lugares == []


def test_detalle_solo_muestra_lugares_de_ese_viaje():
    repositorio = RepositorioFalso()
    europa = repositorio.agregar_viaje("Europa")
    japon = repositorio.agregar_viaje("Japón")
    agregar = AgregarLugar(repositorio)
    agregar(europa, "Coliseo", "Anfiteatro", "Roma", CATEGORIAS[0], "2026-06-12")
    agregar(japon, "Fushimi Inari", "Santuario", "Kioto", CATEGORIAS[0], "2026-06-15")
    detalle = ObtenerDetalleViaje(repositorio)(europa.id)
    assert [l.nombre for l in detalle.lugares] == ["Coliseo"]
