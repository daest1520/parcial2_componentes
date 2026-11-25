from fastapi import APIRouter, HTTPException, status
from app.database import get_connection
from app.schemas import TripCreate
from app.utils import new_id, now_iso

router = APIRouter(prefix="/api/trips", tags=["Viajes"])


@router.get("", summary="Consultar todos los viajes")
def get_trips():
    with get_connection() as db:
        rows = db.execute("SELECT * FROM trips ORDER BY startDate ASC").fetchall()
    return [dict(row) for row in rows]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Crear un viaje")
def create_trip(payload: TripCreate):
    if payload.endDate < payload.startDate:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin debe ser igual o posterior a la fecha de inicio.",
        )

    timestamp = now_iso()
    trip = {
        "id": new_id(),
        "name": payload.name.strip(),
        "destination": payload.destination.strip(),
        "startDate": payload.startDate.isoformat(),
        "endDate": payload.endDate.isoformat(),
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }
    with get_connection() as db:
        db.execute(
            """INSERT INTO trips
            (id, name, destination, startDate, endDate, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            tuple(trip.values()),
        )
    return trip


@router.get("/{trip_id}", summary="Consultar un viaje y sus lugares")
def get_trip(trip_id: str):
    with get_connection() as db:
        trip_row = db.execute(
            "SELECT * FROM trips WHERE id = ?", (trip_id,)
        ).fetchone()
        if trip_row is None:
            raise HTTPException(status_code=404, detail="Viaje no encontrado.")

        place_rows = db.execute(
            """SELECT p.id, p.tripId, p.name, p.description, p.city,
                      p.categoryId, p.tentativeDate, p.createdAt, p.updatedAt,
                      c.name AS categoryName, c.description AS categoryDescription
               FROM places p
               JOIN categories c ON c.id = p.categoryId
               WHERE p.tripId = ?
               ORDER BY p.tentativeDate ASC""",
            (trip_id,),
        ).fetchall()

    places = []
    for row in place_rows:
        place = dict(row)
        place["category"] = {
            "id": place["categoryId"],
            "name": place.pop("categoryName"),
            "description": place.pop("categoryDescription"),
        }
        places.append(place)

    trip = dict(trip_row)
    trip["places"] = places
    trip["placesCount"] = len(places)
    return trip
