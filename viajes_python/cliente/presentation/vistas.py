import queue
import tkinter as tk
from tkinter import ttk

from cliente.domain.validaciones import formatear_fecha

AZUL = "#1565C0"
AZUL_CLARO = "#E3F0FC"
BLANCO = "#FFFFFF"
TEXTO = "#1A1C1E"
GRIS = "#5F6670"
BORDE = "#E1E4E8"
ROJO = "#C62828"
VERDE = "#2E7D32"
FUENTE = "Segoe UI"


def boton(padre, texto, accion, secundario=False):
    fondo, color = (AZUL_CLARO, AZUL) if secundario else (AZUL, BLANCO)
    widget = tk.Button(padre, text=texto, command=accion, bg=fondo, fg=color, relief="flat",
                       font=(FUENTE, 11, "bold"), pady=8, cursor="hand2",
                       activebackground=fondo, activeforeground=color)
    return widget


def etiqueta(padre, texto="", tamano=10, negrita=False, color=TEXTO):
    return tk.Label(padre, text=texto, bg=BLANCO, fg=color, anchor="w", justify="left",
                    wraplength=340, font=(FUENTE, tamano, "bold" if negrita else "normal"))


def campo(padre, titulo, ayuda=""):
    etiqueta(padre, titulo).pack(fill="x", pady=(8, 2))
    variable = tk.StringVar()
    tk.Entry(padre, textvariable=variable, font=(FUENTE, 11), relief="solid", bd=1).pack(fill="x", ipady=5)
    if ayuda:
        etiqueta(padre, ayuda, 8, color=GRIS).pack(fill="x")
    return variable


def tarjeta(padre, al_presionar=None):
    marco = tk.Frame(padre, bg=BLANCO, highlightthickness=1, highlightbackground=BORDE)
    marco.pack(fill="x", pady=(0, 8))
    contenido = tk.Frame(marco, bg=BLANCO)
    contenido.pack(fill="x", padx=12, pady=10)
    if al_presionar:
        def activar():
            for widget in (marco, contenido, *contenido.winfo_children()):
                widget.bind("<Button-1>", lambda _evento: al_presionar())
                widget.config(cursor="hand2")
        return contenido, activar
    return contenido, lambda: None


class ListaConScroll(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre, bg=BLANCO)
        lienzo = tk.Canvas(self, bg=BLANCO, highlightthickness=0)
        barra = tk.Scrollbar(self, command=lienzo.yview)
        self.contenido = tk.Frame(lienzo, bg=BLANCO)
        self.contenido.bind("<Configure>", lambda _e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        ventana = lienzo.create_window((0, 0), window=self.contenido, anchor="nw")
        lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(ventana, width=e.width))
        lienzo.configure(yscrollcommand=barra.set)
        lienzo.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

    def limpiar(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()


class Pantalla(tk.Frame):
    def __init__(self, navegador):
        super().__init__(navegador.ventana, bg=BLANCO)
        self.navegador = navegador
        self.fabrica = navegador.fabrica
        self.activa = True
        self.cancelaciones = []

    def observar(self, estado, dibujar):
        cola = queue.SimpleQueue()
        self.cancelaciones.append(estado.observar(cola.put))

        def revisar():
            if not self.activa:
                return
            ultimo = None
            while not cola.empty():
                ultimo = cola.get()
            if ultimo is not None:
                dibujar(ultimo)
            if self.activa:
                self.after(50, revisar)

        revisar()

    def encabezado(self, titulo, con_volver=True):
        if con_volver:
            volver = etiqueta(self, "←  Volver", color=GRIS)
            volver.config(cursor="hand2")
            volver.pack(fill="x", padx=20, pady=(16, 0))
            volver.bind("<Button-1>", lambda _e: self.navegador.volver())
        texto = etiqueta(self, titulo, 20, True)
        texto.pack(fill="x", padx=20, pady=(8, 10))
        return texto

    def al_volver(self):
        pass

    def destroy(self):
        self.activa = False
        for cancelar in self.cancelaciones:
            cancelar()
        super().destroy()


class Navegador:
    def __init__(self, ventana, fabrica):
        self.ventana = ventana
        self.fabrica = fabrica
        self.pila = []

    def ir_a(self, clase_pantalla, *argumentos):
        if self.pila:
            self.pila[-1].pack_forget()
        pantalla = clase_pantalla(self, *argumentos)
        pantalla.pack(fill="both", expand=True)
        self.pila.append(pantalla)

    def reemplazar(self, clase_pantalla, *argumentos):
        self.pila.pop().destroy()
        self.ir_a(clase_pantalla, *argumentos)

    def volver(self):
        if len(self.pila) > 1:
            self.pila.pop().destroy()
            self.pila[-1].pack(fill="both", expand=True)
            self.pila[-1].al_volver()


class ListaViajesPantalla(Pantalla):
    def __init__(self, navegador):
        super().__init__(navegador)
        self.viewmodel = self.fabrica.lista_viajes()
        etiqueta(self, "Mis viajes", 22, True).pack(fill="x", padx=20, pady=(28, 12))
        boton(self, "Crear viaje", lambda: navegador.ir_a(CrearViajePantalla)).pack(fill="x", padx=20)
        boton(self, "Ver categorías", lambda: navegador.ir_a(CategoriasPantalla), secundario=True).pack(
            fill="x", padx=20, pady=(8, 0))
        etiqueta(self, "Viajes registrados", 14, True).pack(fill="x", padx=20, pady=(20, 6))
        self.mensaje = etiqueta(self, color=GRIS)
        self.mensaje.pack(fill="x", padx=20)
        self.lista = ListaConScroll(self)
        self.lista.pack(fill="both", expand=True, padx=(20, 6), pady=(0, 10))
        self.observar(self.viewmodel.estado, self.dibujar)
        self.viewmodel.cargar_viajes()

    def al_volver(self):
        self.viewmodel.cargar_viajes()

    def dibujar(self, estado):
        if estado.error:
            self.mensaje.config(text=estado.error, fg=ROJO)
        elif estado.cargando and not estado.viajes:
            self.mensaje.config(text="Cargando viajes…", fg=GRIS)
        elif not estado.viajes:
            self.mensaje.config(text="No hay viajes registrados", fg=GRIS)
        else:
            self.mensaje.config(text="")
        self.lista.limpiar()
        for viaje in estado.viajes:
            contenido, activar = tarjeta(
                self.lista.contenido, lambda vid=viaje.id: self.navegador.ir_a(DetalleViajePantalla, vid))
            etiqueta(contenido, viaje.nombre, 12, True).pack(fill="x")
            etiqueta(contenido, f"Destino: {viaje.destino}").pack(fill="x")
            etiqueta(contenido, f"{formatear_fecha(viaje.fecha_inicio)} al {formatear_fecha(viaje.fecha_fin)}",
                     9, color=GRIS).pack(fill="x")
            activar()


class CrearViajePantalla(Pantalla):
    def __init__(self, navegador):
        super().__init__(navegador)
        self.viewmodel = self.fabrica.crear_viaje()
        self.encabezado("Crear viaje")
        formulario = tk.Frame(self, bg=BLANCO)
        formulario.pack(fill="x", padx=20)
        self.nombre = campo(formulario, "Nombre")
        self.destino = campo(formulario, "Destino")
        self.fecha_inicio = campo(formulario, "Fecha de inicio", "AAAA-MM-DD")
        self.fecha_fin = campo(formulario, "Fecha de finalización", "AAAA-MM-DD")
        self.mensaje = etiqueta(self, color=ROJO)
        self.mensaje.pack(fill="x", padx=20, pady=8)
        self.boton_guardar = boton(self, "Guardar", self.guardar)
        self.boton_guardar.pack(fill="x", padx=20)
        self.observar(self.viewmodel.estado, self.dibujar)

    def guardar(self):
        self.viewmodel.guardar_viaje(
            self.nombre.get(), self.destino.get(), self.fecha_inicio.get(), self.fecha_fin.get())

    def dibujar(self, estado):
        self.mensaje.config(text=estado.error or "")
        self.boton_guardar.config(state="disabled" if estado.guardando else "normal")
        if estado.viaje_guardado_id:
            self.navegador.reemplazar(DetalleViajePantalla, estado.viaje_guardado_id)


class DetalleViajePantalla(Pantalla):
    def __init__(self, navegador, viaje_id):
        super().__init__(navegador)
        self.viewmodel = self.fabrica.detalle_viaje(viaje_id)
        self.titulo = self.encabezado("Detalle del viaje")
        boton(self, "Agregar lugar", lambda: navegador.ir_a(AgregarLugarPantalla, viaje_id)).pack(
            side="bottom", fill="x", padx=20, pady=14)
        self.informacion = tk.Frame(self, bg=BLANCO)
        self.informacion.pack(fill="x", padx=20)
        self.lista = ListaConScroll(self)
        self.lista.pack(fill="both", expand=True, padx=(20, 6))
        self.observar(self.viewmodel.estado, self.dibujar)
        self.viewmodel.cargar_detalle()

    def al_volver(self):
        self.viewmodel.cargar_detalle()

    def dibujar(self, estado):
        for widget in self.informacion.winfo_children():
            widget.destroy()
        if estado.error:
            etiqueta(self.informacion, estado.error, color=ROJO).pack(fill="x")
        if estado.detalle is None:
            return
        viaje, lugares = estado.detalle.viaje, estado.detalle.lugares
        self.titulo.config(text=viaje.nombre)
        etiqueta(self.informacion, f"Destino: {viaje.destino}", 11).pack(fill="x")
        etiqueta(self.informacion, f"{formatear_fecha(viaje.fecha_inicio)} al {formatear_fecha(viaje.fecha_fin)}",
                 10, color=GRIS).pack(fill="x", pady=(2, 12))
        etiqueta(self.informacion, f"Lugares a visitar ({len(lugares)})", 13, True).pack(fill="x", pady=(0, 6))
        self.lista.limpiar()
        if not lugares:
            etiqueta(self.lista.contenido, "Aún no hay lugares registrados", color=GRIS).pack(fill="x")
        for lugar in lugares:
            contenido, _ = tarjeta(self.lista.contenido)
            etiqueta(contenido, lugar.nombre, 11, True).pack(fill="x")
            etiqueta(contenido, f"{lugar.categoria.nombre} · {lugar.ciudad} · {formatear_fecha(lugar.fecha_visita)}",
                     9, color=AZUL).pack(fill="x")
            etiqueta(contenido, lugar.descripcion, 9, color=GRIS).pack(fill="x")


class AgregarLugarPantalla(Pantalla):
    def __init__(self, navegador, viaje_id):
        super().__init__(navegador)
        self.viewmodel = self.fabrica.agregar_lugar(viaje_id)
        self.encabezado("Agregar lugar")
        formulario = tk.Frame(self, bg=BLANCO)
        formulario.pack(fill="x", padx=20)
        self.nombre = campo(formulario, "Nombre")
        self.descripcion = campo(formulario, "Descripción")
        self.ciudad = campo(formulario, "Ciudad")
        etiqueta(formulario, "Categoría").pack(fill="x", pady=(8, 2))
        self.categoria = ttk.Combobox(formulario, state="readonly", font=(FUENTE, 11))
        self.categoria.pack(fill="x", ipady=3)
        self.fecha_visita = campo(formulario, "Fecha tentativa de visita", "AAAA-MM-DD")
        self.rango = etiqueta(formulario, "", 9, color=AZUL)
        self.rango.pack(fill="x")
        self.mensaje = etiqueta(self, color=ROJO)
        self.mensaje.pack(fill="x", padx=20, pady=8)
        self.boton_guardar = boton(self, "Guardar", self.guardar)
        self.boton_guardar.pack(fill="x", padx=20)
        self.categorias_mostradas = None
        self.observar(self.viewmodel.estado, self.dibujar)
        self.viewmodel.cargar_datos()

    def guardar(self):
        self.viewmodel.guardar_lugar(
            self.nombre.get(), self.descripcion.get(), self.ciudad.get(),
            self.categoria.current(), self.fecha_visita.get())

    def dibujar(self, estado):
        if estado.categorias != self.categorias_mostradas:
            self.categorias_mostradas = estado.categorias
            self.categoria["values"] = [c.nombre for c in estado.categorias]
        if estado.viaje:
            self.rango.config(text=f"Debe estar entre {formatear_fecha(estado.viaje.fecha_inicio)} "
                                   f"y {formatear_fecha(estado.viaje.fecha_fin)}")
        if estado.guardado:
            self.mensaje.config(text="Lugar guardado", fg=VERDE)
            self.boton_guardar.config(state="disabled")
            self.after(700, self.navegador.volver)
            return
        self.mensaje.config(text=estado.error or "", fg=ROJO)
        self.boton_guardar.config(state="disabled" if estado.guardando or estado.cargando else "normal")


class CategoriasPantalla(Pantalla):
    def __init__(self, navegador):
        super().__init__(navegador)
        self.viewmodel = self.fabrica.categorias()
        self.encabezado("Categorías")
        self.mensaje = etiqueta(self, color=GRIS)
        self.mensaje.pack(fill="x", padx=20)
        self.lista = ListaConScroll(self)
        self.lista.pack(fill="both", expand=True, padx=(20, 6), pady=(0, 10))
        self.observar(self.viewmodel.estado, self.dibujar)
        self.viewmodel.cargar_categorias()

    def dibujar(self, estado):
        if estado.error:
            self.mensaje.config(text=estado.error, fg=ROJO)
        else:
            self.mensaje.config(text="Cargando…" if estado.cargando else "", fg=GRIS)
        self.lista.limpiar()
        for categoria in estado.categorias:
            contenido, _ = tarjeta(self.lista.contenido)
            etiqueta(contenido, categoria.nombre, 11, True).pack(fill="x")
            etiqueta(contenido, categoria.descripcion, 9, color=GRIS).pack(fill="x")
