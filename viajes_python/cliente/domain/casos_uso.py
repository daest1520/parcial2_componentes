from cliente.domain import validaciones


class ObtenerViajes:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def __call__(self):
        return self.repositorio.obtener_viajes()


class CrearViaje:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def __call__(self, nombre, destino, fecha_inicio, fecha_fin):
        datos = validaciones.validar_viaje(nombre, destino, fecha_inicio, fecha_fin)
        return self.repositorio.guardar_viaje(*datos)


class ObtenerDetalleViaje:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def __call__(self, viaje_id):
        return self.repositorio.obtener_detalle_viaje(viaje_id)


class AgregarLugar:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def __call__(self, viaje, nombre, descripcion, ciudad, categoria, fecha_visita):
        datos = validaciones.validar_lugar(viaje, nombre, descripcion, ciudad, categoria, fecha_visita)
        return self.repositorio.guardar_lugar(viaje.id, *datos)


class ObtenerCategorias:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def __call__(self):
        return self.repositorio.obtener_categorias()
