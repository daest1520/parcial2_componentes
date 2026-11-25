# API Planificador de viajes

Backend REST para la aplicación de planificación de viajes, desarrollado con **Python, FastAPI y SQLite**.

La base de datos es un archivo local (`data/viajes.db`). No requiere instalar SQLite Server, MongoDB ni configurar otro servicio. Se utiliza el módulo `sqlite3` incluido en Python.

## 1. Requisitos

- Python **3.10 o superior**.
- pip.

## 2. Instalación y ejecución

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Windows

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

La base de datos, sus tablas y las categorías iniciales se crean automáticamente al iniciar la API.

Para cargar los datos de demostración (viaje Europa 2026 y tres lugares):

```bash
python seed.py
```

**Atención:** `python seed.py` elimina los viajes y lugares existentes y vuelve a cargar los datos de ejemplo. No lo ejecutes si deseas conservar los registros.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Estado: http://localhost:8000/api/health

## 3. Estructura de datos

La información se almacena en tres tablas relacionadas:

- **trips**: datos propios de cada viaje.
- **categories**: catálogo de categorías (`id`, `name`, `description`).
- **places**: lugares que almacena `tripId` y `categoryId` como claves foráneas.

Relaciones:

```text
trips (1) -------- (N) places (N) -------- (1) categories
```

## 4. Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/trips` | Consultar todos los viajes |
| POST | `/api/trips` | Guardar un viaje |
| GET | `/api/trips/{id}` | Consultar el detalle de un viaje y sus lugares |
| GET | `/api/places?tripId={id}` | Consultar lugares, opcionalmente filtrados por viaje |
| POST | `/api/places` | Crear un lugar para un viaje |
| GET | `/api/categories` | Consultar categorías desde SQLite |
| GET | `/api/health` | Verificar el estado de la API |

## 5. Ejemplos de consumo

### Crear viaje — `POST /api/trips`

```json
{
  "name": "Europa 2026",
  "destination": "Italia",
  "startDate": "2026-06-10",
  "endDate": "2026-06-20"
}
```

La respuesta incluye el `id` generado para el viaje. Se utiliza como `tripId` al registrar lugares.

### Consultar categorías — `GET /api/categories`

Respuesta de ejemplo:

```json
[
  { "id": 1, "name": "Histórico", "description": "Monumentos, sitios y patrimonio histórico." },
  { "id": 2, "name": "Cultural", "description": "Museos, teatros, galerías y expresiones culturales." }
]
```

### Crear lugar — `POST /api/places`

```json
{
  "tripId": "ID_DEVUELTO_AL_CREAR_EL_VIAJE",
  "name": "Coliseo Romano",
  "description": "Anfiteatro romano, uno de los principales atractivos de Roma.",
  "city": "Roma",
  "categoryId": 1,
  "tentativeDate": "2026-06-12"
}
```

El cliente debe consultar primero `/api/categories` y enviar el `id` numérico de la categoría seleccionada. La respuesta del lugar incluye `categoryId` y el objeto `category` con sus datos descriptivos.

### Consultar detalle de viaje — `GET /api/trips/{id}`

Devuelve el viaje, el arreglo `places` con sus lugares y `placesCount`. Cada lugar incluye su categoría relacionada.

## 6. Validaciones

- Todos los campos requeridos deben estar presentes.
- La fecha final del viaje no puede ser anterior a la fecha inicial.
- El lugar debe estar asociado a un viaje existente.
- `categoryId` debe ser un número entero y existir en la tabla `categories`.
- La fecha tentativa del lugar debe estar dentro del período del viaje.
- SQLite refuerza las relaciones mediante claves foráneas.

## 7. Estructura del proyecto

```text
viajes_api_python/
├── app/
│   ├── routers/
│   │   ├── categories.py
│   │   ├── places.py
│   │   └── trips.py
│   ├── categories.py
│   ├── database.py
│   ├── main.py
│   ├── schemas.py
│   └── utils.py
├── data/
├── requirements.txt
├── seed.py
├── run.py
└── README.md
```

## 8. Conexión desde Android

- Emulador Android: `http://10.0.2.2:8000`.
- Teléfono físico: utiliza la IP local del computador donde corre FastAPI; ambos dispositivos deben estar en la misma red Wi-Fi.

La API está preparada para consumirse desde Android con Kotlin, Retrofit y MVVM.
