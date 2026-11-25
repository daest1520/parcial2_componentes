from datetime import date

from cliente.domain.modelos import ErrorValidacion


def obligatorio(valor, campo):
    if valor is None or not str(valor).strip():
        raise ErrorValidacion(f"El campo {campo} es obligatorio")
    return str(valor).strip()


def convertir_fecha(texto, campo):
    valor = obligatorio(texto, campo)
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ErrorValidacion(f"{campo} debe tener el formato AAAA-MM-DD") from None


def formatear_fecha(fecha):
    return fecha.strftime("%d/%m/%Y")


def validar_viaje(nombre, destino, texto_inicio, texto_fin):
    nombre = obligatorio(nombre, "Nombre")
    destino = obligatorio(destino, "Destino")
    fecha_inicio = convertir_fecha(texto_inicio, "Fecha de inicio")
    fecha_fin = convertir_fecha(texto_fin, "Fecha de finalización")
    if fecha_inicio > fecha_fin:
        raise ErrorValidacion("La fecha de inicio no puede ser posterior a la fecha de finalización")
    return nombre, destino, fecha_inicio, fecha_fin


def validar_lugar(viaje, nombre, descripcion, ciudad, categoria, texto_fecha):
    nombre = obligatorio(nombre, "Nombre")
    descripcion = obligatorio(descripcion, "Descripción")
    ciudad = obligatorio(ciudad, "Ciudad")
    if categoria is None:
        raise ErrorValidacion("Debe seleccionar una categoría")
    fecha_visita = convertir_fecha(texto_fecha, "Fecha tentativa")
    if fecha_visita < viaje.fecha_inicio or fecha_visita > viaje.fecha_fin:
        raise ErrorValidacion(
            f"La fecha debe estar entre {formatear_fecha(viaje.fecha_inicio)} "
            f"y {formatear_fecha(viaje.fecha_fin)}"
        )
    return nombre, descripcion, ciudad, categoria.id, fecha_visita
