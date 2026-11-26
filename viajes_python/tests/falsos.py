from datetime import date

from cliente.domain.modelos import Categoria, DetalleViaje, Lugar, Viaje
from cliente.domain.repositorio import ViajeRepositorio

CATEGORIAS = [Categoria(1, "Histórico", "Monumentos"), Categoria(2, "Natural", "Parques")]


class RepositorioFalso(ViajeRepositorio):
    def __init__(self):
        self.viajes = []
        self.lugares = []
        self.error = None

    def obtener_viajes(self):
        if self.error:
            raise self.error
        return list(self.viajes)

    def guardar_viaje(self, nombre, destino, fecha_inicio, fecha_fin):
        viaje = Viaje(f"v{len(self.viajes) + 1}", nombre, destino, fecha_inicio, fecha_fin)
        self.viajes.append(viaje)
        return viaje

    def obtener_detalle_viaje(self, viaje_id):
        viaje = next(v for v in self.viajes if v.id == viaje_id)
        return DetalleViaje(viaje, [l for l in self.lugares if l.viaje_id == viaje_id])

    def guardar_lugar(self, viaje_id, nombre, descripcion, ciudad, categoria_id, fecha_visita):
        categoria = next(c for c in CATEGORIAS if c.id == categoria_id)
        lugar = Lugar(f"l{len(self.lugares) + 1}", viaje_id, nombre, descripcion, ciudad, categoria, fecha_visita)
        self.lugares.append(lugar)
        return lugar

    def obtener_categorias(self):
        return list(CATEGORIAS)

    def agregar_viaje(self, nombre="Europa"):
        viaje = Viaje(f"v{len(self.viajes) + 1}", nombre, "Italia", date(2026, 6, 10), date(2026, 6, 20))
        self.viajes.append(viaje)
        return viaje
