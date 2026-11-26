import threading
from concurrent.futures import ThreadPoolExecutor


class EstadoObservable:
    def __init__(self, valor_inicial):
        self.valor = valor_inicial
        self.observadores = []
        self.candado = threading.Lock()

    def observar(self, funcion):
        with self.candado:
            self.observadores.append(funcion)
        funcion(self.valor)
        return lambda: self.observadores.remove(funcion) if funcion in self.observadores else None

    def emitir(self, nuevo_valor):
        with self.candado:
            if nuevo_valor == self.valor:
                return
            self.valor = nuevo_valor
            observadores = list(self.observadores)
        for funcion in observadores:
            funcion(nuevo_valor)


class EjecutorSegundoPlano:
    hilos = ThreadPoolExecutor(max_workers=4)

    def ejecutar(self, tarea):
        self.hilos.submit(tarea)


class EjecutorInmediato:
    def ejecutar(self, tarea):
        tarea()
