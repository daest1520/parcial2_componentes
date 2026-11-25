from abc import ABC, abstractmethod


class ViajeRepositorio(ABC):

    @abstractmethod
    def obtener_viajes(self):
        pass

    @abstractmethod
    def guardar_viaje(self, nombre, destino, fecha_inicio, fecha_fin):
        pass

    @abstractmethod
    def obtener_detalle_viaje(self, viaje_id):
        pass

    @abstractmethod
    def guardar_lugar(self, viaje_id, nombre, descripcion, ciudad, categoria_id, fecha_visita):
        pass

    @abstractmethod
    def obtener_categorias(self):
        pass
