import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import tkinter as tk

from cliente.data.repositorio_impl import crear_repositorio
from cliente.presentation.viewmodels import FabricaViewModels
from cliente.presentation.vistas import BLANCO, ListaViajesPantalla, Navegador


def crear_ventana():
    ventana = tk.Tk()
    ventana.title("Planificador de Viajes")
    ventana.geometry("400x720")
    ventana.configure(bg=BLANCO)
    return ventana


def main():
    ventana = crear_ventana()
    navegador = Navegador(ventana, FabricaViewModels(crear_repositorio()))
    navegador.ir_a(ListaViajesPantalla)
    ventana.mainloop()


if __name__ == "__main__":
    main()
