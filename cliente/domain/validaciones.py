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

