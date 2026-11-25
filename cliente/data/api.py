from uplink import Body, Consumer, Path, get, json, post, response_handler, returns, timeout


class ErrorApi(Exception):
    pass


def revisar_respuesta(respuesta):
    if respuesta.status_code >= 400:
        try:
            detalle = respuesta.json().get("detail", "Error del servidor")
        except ValueError:
            detalle = "Error del servidor"
        if isinstance(detalle, list):
            detalle = "Datos inválidos"
        raise ErrorApi(str(detalle))
    return respuesta


@response_handler(revisar_respuesta)
@timeout(10)
class ViajeApi(Consumer):

    @returns.json
    @get("api/trips")
    def obtener_viajes(self):
        pass

    @json
    @returns.json
    @post("api/trips")
    def crear_viaje(self, cuerpo: Body):
        pass

    @returns.json
    @get("api/trips/{viaje_id}")
    def obtener_viaje(self, viaje_id: Path("viaje_id")):
        pass



def crear_api(url_base):
    if not url_base.endswith("/"):
        url_base += "/"
    return ViajeApi(base_url=url_base)
