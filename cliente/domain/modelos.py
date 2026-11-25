from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Categoria:
    id: int
    nombre: str
    descripcion: str = ""


@dataclass(frozen=True)
class Viaje:
    id: str
    nombre: str
    destino: str
    fecha_inicio: date
    fecha_fin: date


@dataclass(frozen=True)
class Lugar:
    id: str
    viaje_id: str
    nombre: str
    descripcion: str
    ciudad: str
    categoria: Categoria
    fecha_visita: date


@dataclass(frozen=True)
class DetalleViaje:
    viaje: Viaje
    lugares: list = field(default_factory=list)


class ErrorApp(Exception):
    pass


class ErrorValidacion(ErrorApp):
    pass


class ErrorConexion(ErrorApp):
    pass


class ErrorServidor(ErrorApp):
    pass
