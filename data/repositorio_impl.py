import os
from datetime import date

import requests

from cliente.data.api import ErrorApi, crear_api
from cliente.data.cache_local import CacheLocal
from cliente.domain.modelos import Categoria, DetalleViaje, ErrorConexion, ErrorServidor, Lugar, Viaje
from cliente.domain.repositorio import ViajeRepositorio


def a_viaje(datos):
    return Viaje(
        datos["id"],
        datos["name"],
        datos["destination"],
        date.fromisoformat(datos["startDate"]),
        date.fromisoformat(datos["endDate"]),
    )


def a_categoria(datos):
    return Categoria(datos["id"], datos["name"], datos.get("description") or "")


def a_lugar(datos):
    if datos.get("category"):
        categoria = a_categoria(datos["category"])
    else:
        categoria = Categoria(datos["categoryId"], "")
    return Lugar(
        datos["id"],
        datos["tripId"],
        datos["name"],
        datos["description"],
        datos["city"],
        categoria,
        date.fromisoformat(datos["tentativeDate"]),
    )


class ViajeRepositorioImpl(ViajeRepositorio):

    def __init__(self, api, cache):
        self.api = api
        self.cache = cache

    def _llamar(self, peticion):
        try:
            return peticion()
        except ErrorApi as error:
            raise ErrorServidor(str(error)) from error
        except requests.RequestException as error:
            raise ErrorConexion("No hay conexión con el servidor") from error

    def _consultar(self, clave, peticion):
        try:
            datos = self._llamar(peticion)
            self.cache.guardar(clave, datos)
            return datos
        except ErrorConexion:
            datos = self.cache.cargar(clave)
            if datos is None:
                raise
            return datos

    def obtener_viajes(self):
        return [a_viaje(d) for d in self._consultar("viajes", self.api.obtener_viajes)]

    def guardar_viaje(self, nombre, destino, fecha_inicio, fecha_fin):
        cuerpo = {
            "name": nombre,
            "destination": destino,
            "startDate": fecha_inicio.isoformat(),
            "endDate": fecha_fin.isoformat(),
        }
        return a_viaje(self._llamar(lambda: self.api.crear_viaje(cuerpo)))

    def obtener_detalle_viaje(self, viaje_id):
        datos = self._consultar(f"viaje_{viaje_id}", lambda: self.api.obtener_viaje(viaje_id))
        return DetalleViaje(a_viaje(datos), [a_lugar(d) for d in datos.get("places", [])])

    def guardar_lugar(self, viaje_id, nombre, descripcion, ciudad, categoria_id, fecha_visita):
        cuerpo = {
            "tripId": viaje_id,
            "name": nombre,
            "description": descripcion,
            "city": ciudad,
            "categoryId": categoria_id,
            "tentativeDate": fecha_visita.isoformat(),
        }
        return a_lugar(self._llamar(lambda: self.api.crear_lugar(cuerpo)))

    def obtener_categorias(self):
        return [a_categoria(d) for d in self._consultar("categorias", self.api.obtener_categorias)]


def crear_repositorio(url_base=None, ruta_cache=None):
    url_base = url_base or os.environ.get("API_BASE_URL", "http://localhost:8000/")
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ruta_cache = ruta_cache or os.path.join(raiz, "cache_viajes.db")
    return ViajeRepositorioImpl(crear_api(url_base), CacheLocal(ruta_cache))
