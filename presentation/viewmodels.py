from dataclasses import dataclass, replace

from cliente.domain.casos_uso import (
    AgregarLugar,
    CrearViaje,
    ObtenerCategorias,
    ObtenerDetalleViaje,
    ObtenerViajes,
)
from cliente.domain.modelos import ErrorApp
from cliente.presentation.estado import EjecutorSegundoPlano, EstadoObservable


class ViewModelBase:
    def __init__(self, ejecutor=None):
        self.ejecutor = ejecutor or EjecutorSegundoPlano()

    def lanzar(self, trabajo, al_fallar):
        def tarea():
            try:
                trabajo()
            except ErrorApp as error:
                al_fallar(str(error))

        self.ejecutor.ejecutar(tarea)


@dataclass(frozen=True)
class EstadoListaViajes:
    cargando: bool = False
    viajes: tuple = ()
    error: str = None


class ListaViajesViewModel(ViewModelBase):
    def __init__(self, obtener_viajes, ejecutor=None):
        super().__init__(ejecutor)
        self.obtener_viajes = obtener_viajes
        self.estado = EstadoObservable(EstadoListaViajes())

    def cargar_viajes(self):
        self.estado.emitir(replace(self.estado.valor, cargando=True, error=None))
        self.lanzar(
            lambda: self.estado.emitir(EstadoListaViajes(viajes=tuple(self.obtener_viajes()))),
            lambda mensaje: self.estado.emitir(EstadoListaViajes(error=mensaje)),
        )


@dataclass(frozen=True)
class EstadoCrearViaje:
    guardando: bool = False
    error: str = None
    viaje_guardado_id: str = None


class CrearViajeViewModel(ViewModelBase):
    def __init__(self, crear_viaje, ejecutor=None):
        super().__init__(ejecutor)
        self.crear_viaje = crear_viaje
        self.estado = EstadoObservable(EstadoCrearViaje())

    def guardar_viaje(self, nombre, destino, fecha_inicio, fecha_fin):
        self.estado.emitir(EstadoCrearViaje(guardando=True))

        def trabajo():
            viaje = self.crear_viaje(nombre, destino, fecha_inicio, fecha_fin)
            self.estado.emitir(EstadoCrearViaje(viaje_guardado_id=viaje.id))

        self.lanzar(trabajo, lambda mensaje: self.estado.emitir(EstadoCrearViaje(error=mensaje)))


@dataclass(frozen=True)
class EstadoDetalleViaje:
    cargando: bool = False
    detalle: object = None
    error: str = None


class DetalleViajeViewModel(ViewModelBase):
    def __init__(self, viaje_id, obtener_detalle_viaje, ejecutor=None):
        super().__init__(ejecutor)
        self.viaje_id = viaje_id
        self.obtener_detalle_viaje = obtener_detalle_viaje
        self.estado = EstadoObservable(EstadoDetalleViaje())

    def cargar_detalle(self):
        self.estado.emitir(replace(self.estado.valor, cargando=True, error=None))
        self.lanzar(
            lambda: self.estado.emitir(EstadoDetalleViaje(detalle=self.obtener_detalle_viaje(self.viaje_id))),
            lambda mensaje: self.estado.emitir(replace(self.estado.valor, cargando=False, error=mensaje)),
        )


@dataclass(frozen=True)
class EstadoAgregarLugar:
    cargando: bool = False
    viaje: object = None
    categorias: tuple = ()
    guardando: bool = False
    error: str = None
    guardado: bool = False


class AgregarLugarViewModel(ViewModelBase):
    def __init__(self, viaje_id, obtener_detalle_viaje, obtener_categorias, agregar_lugar, ejecutor=None):
        super().__init__(ejecutor)
        self.viaje_id = viaje_id
        self.obtener_detalle_viaje = obtener_detalle_viaje
        self.obtener_categorias = obtener_categorias
        self.agregar_lugar = agregar_lugar
        self.estado = EstadoObservable(EstadoAgregarLugar())

    def cargar_datos(self):
        self.estado.emitir(EstadoAgregarLugar(cargando=True))

        def trabajo():
            viaje = self.obtener_detalle_viaje(self.viaje_id).viaje
            categorias = tuple(self.obtener_categorias())
            self.estado.emitir(EstadoAgregarLugar(viaje=viaje, categorias=categorias))

        self.lanzar(trabajo, lambda mensaje: self.estado.emitir(replace(self.estado.valor, cargando=False, error=mensaje)))

    def guardar_lugar(self, nombre, descripcion, ciudad, indice_categoria, fecha_visita):
        estado = self.estado.valor
        if estado.viaje is None:
            return
        categoria = estado.categorias[indice_categoria] if 0 <= indice_categoria < len(estado.categorias) else None
        self.estado.emitir(replace(estado, guardando=True, error=None))

        def trabajo():
            self.agregar_lugar(estado.viaje, nombre, descripcion, ciudad, categoria, fecha_visita)
            self.estado.emitir(replace(self.estado.valor, guardando=False, guardado=True))

        self.lanzar(trabajo, lambda mensaje: self.estado.emitir(replace(self.estado.valor, guardando=False, error=mensaje)))


@dataclass(frozen=True)
class EstadoCategorias:
    cargando: bool = False
    categorias: tuple = ()
    error: str = None


class CategoriasViewModel(ViewModelBase):
    def __init__(self, obtener_categorias, ejecutor=None):
        super().__init__(ejecutor)
        self.obtener_categorias = obtener_categorias
        self.estado = EstadoObservable(EstadoCategorias())

    def cargar_categorias(self):
        self.estado.emitir(EstadoCategorias(cargando=True))
        self.lanzar(
            lambda: self.estado.emitir(EstadoCategorias(categorias=tuple(self.obtener_categorias()))),
            lambda mensaje: self.estado.emitir(EstadoCategorias(error=mensaje)),
        )


class FabricaViewModels:
    def __init__(self, repositorio, ejecutor=None):
        self.repositorio = repositorio
        self.ejecutor = ejecutor or EjecutorSegundoPlano()

    def lista_viajes(self):
        return ListaViajesViewModel(ObtenerViajes(self.repositorio), self.ejecutor)

    def crear_viaje(self):
        return CrearViajeViewModel(CrearViaje(self.repositorio), self.ejecutor)

    def detalle_viaje(self, viaje_id):
        return DetalleViajeViewModel(viaje_id, ObtenerDetalleViaje(self.repositorio), self.ejecutor)

    def agregar_lugar(self, viaje_id):
        return AgregarLugarViewModel(
            viaje_id,
            ObtenerDetalleViaje(self.repositorio),
            ObtenerCategorias(self.repositorio),
            AgregarLugar(self.repositorio),
            self.ejecutor,
        )

    def categorias(self):
        return CategoriasViewModel(ObtenerCategorias(self.repositorio), self.ejecutor)
