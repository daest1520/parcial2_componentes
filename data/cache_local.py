import json
import sqlite3
import threading


class CacheLocal:
    def __init__(self, ruta="cache_viajes.db"):
        self.conexion = sqlite3.connect(ruta, check_same_thread=False)
        self.candado = threading.Lock()
        with self.candado:
            self.conexion.execute("CREATE TABLE IF NOT EXISTS cache (clave TEXT PRIMARY KEY, datos TEXT)")
            self.conexion.commit()

    def guardar(self, clave, datos):
        with self.candado:
            self.conexion.execute("INSERT OR REPLACE INTO cache VALUES (?, ?)", (clave, json.dumps(datos)))
            self.conexion.commit()

    def cargar(self, clave):
        with self.candado:
            fila = self.conexion.execute("SELECT datos FROM cache WHERE clave = ?", (clave,)).fetchone()
        return json.loads(fila[0]) if fila else None
