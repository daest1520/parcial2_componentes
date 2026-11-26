from cliente.domain.modelos import ErrorConexion
from cliente.presentation.estado import EjecutorInmediato
from cliente.presentation.viewmodels import FabricaViewModels
from tests.falsos import RepositorioFalso


def crear_fabrica():
    repositorio = RepositorioFalso()
    return repositorio, FabricaViewModels(repositorio, EjecutorInmediato())


def test_lista_muestra_los_viajes():
    repositorio, fabrica = crear_fabrica()
    repositorio.agregar_viaje("Europa")
    viewmodel = fabrica.lista_viajes()
    viewmodel.cargar_viajes()
    assert viewmodel.estado.valor.viajes[0].nombre == "Europa"
    assert viewmodel.estado.valor.cargando is False


def test_lista_muestra_error_sin_conexion():
    repositorio, fabrica = crear_fabrica()
    repositorio.error = ErrorConexion("No hay conexión con el servidor")
    viewmodel = fabrica.lista_viajes()
    viewmodel.cargar_viajes()
    assert viewmodel.estado.valor.error == "No hay conexión con el servidor"


def test_crear_viaje_valido():
    repositorio, fabrica = crear_fabrica()
    viewmodel = fabrica.crear_viaje()
    viewmodel.guardar_viaje("Europa", "Italia", "2026-06-10", "2026-06-20")
    assert viewmodel.estado.valor.viaje_guardado_id == "v1"


def test_crear_viaje_invalido_muestra_error():
    repositorio, fabrica = crear_fabrica()
    viewmodel = fabrica.crear_viaje()
    viewmodel.guardar_viaje("", "Italia", "2026-06-10", "2026-06-20")
    assert viewmodel.estado.valor.error == "El campo Nombre es obligatorio"
    assert repositorio.viajes == []


def test_detalle_carga_el_viaje():
    repositorio, fabrica = crear_fabrica()
    viaje = repositorio.agregar_viaje()
    viewmodel = fabrica.detalle_viaje(viaje.id)
    viewmodel.cargar_detalle()
    assert viewmodel.estado.valor.detalle.viaje == viaje


def test_agregar_lugar_valido():
    repositorio, fabrica = crear_fabrica()
    viaje = repositorio.agregar_viaje()
    viewmodel = fabrica.agregar_lugar(viaje.id)
    viewmodel.cargar_datos()
    assert len(viewmodel.estado.valor.categorias) == 2
    viewmodel.guardar_lugar("Coliseo", "Anfiteatro", "Roma", 0, "2026-06-12")
    assert viewmodel.estado.valor.guardado is True
    assert len(repositorio.lugares) == 1


def test_agregar_lugar_fuera_del_viaje_muestra_error():
    repositorio, fabrica = crear_fabrica()
    viaje = repositorio.agregar_viaje()
    viewmodel = fabrica.agregar_lugar(viaje.id)
    viewmodel.cargar_datos()
    viewmodel.guardar_lugar("Coliseo", "Anfiteatro", "Roma", 0, "2026-12-01")
    assert "debe estar entre" in viewmodel.estado.valor.error
    assert repositorio.lugares == []


def test_categorias():
    repositorio, fabrica = crear_fabrica()
    viewmodel = fabrica.categorias()
    viewmodel.cargar_categorias()
    assert [c.nombre for c in viewmodel.estado.valor.categorias] == ["Histórico", "Natural"]
