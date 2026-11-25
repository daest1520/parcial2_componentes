from fastapi import APIRouter, HTTPException, Query, status
from app.database import get_connection
from app.schemas import PlaceCreate
from app.utils import new_id, now_iso

router = APIRouter(prefix="/api/places", tags=["Lugares"])

SELECT_PLACES = """
    SELECT p.id, p.tripId, p.name, p.description, p.city, p.categoryId,
           p.tentativeDate, p.createdAt, p.updatedAt,
           c.name AS categoryName, c.description AS categoryDescription
    FROM places p
    JOIN categories c ON c.id = p.categoryId
"""


def place_response(row):
    place = dict(row)
    place["category"] = {
        "id": place["categoryId"],
        "name": place.pop("categoryName"),
        "description": place.pop("categoryDescription"),
    }
    return place


@router.post("", status_code=status.HTTP_201_CREATED, summary="Agregar un lugar a un viaje")
def create_place(payload: PlaceCreate):
    timestamp = now_iso()
    place_date = payload.tentativeDate.isoformat()

    with get_connection() as db:
        trip = db.execute(
            "SELECT * FROM trips WHERE id = ?", (payload.tripId,)
        ).fetchone()
        if trip is None:
            raise HTTPException(status_code=404, detail="No existe el viaje indicado.")

        category = db.execute(
            "SELECT id FROM categories WHERE id = ?", (payload.categoryId,)
        ).fetchone()
        if category is None:
            raise HTTPException(
                status_code=400,
                detail="El categoryId no es válido. Consulta GET /api/categories.",
            )

        if place_date < trip["startDate"] or place_date > trip["endDate"]:
            raise HTTPException(
                status_code=400,
                detail="La fecha tentativa debe estar dentro del rango de fechas del viaje.",
            )

        place = {
            "id": new_id(),
            "tripId": payload.tripId,
            "name": payload.name.strip(),
            "description": payload.description.strip(),
            "city": payload.city.strip(),
            "categoryId": payload.categoryId,
            "tentativeDate": place_date,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }
        db.execute(
            """INSERT INTO places
            (id, tripId, name, description, city, categoryId,
             tentativeDate, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            tuple(place.values()),
        )
        row = db.execute(
            SELECT_PLACES + " WHERE p.id = ?", (place["id"],)
        ).fetchone()

    return place_response(row)


@router.get("", summary="Consultar lugares, opcionalmente filtrados por viaje")
def get_places(tripId: str | None = Query(default=None)):
    with get_connection() as db:
        if tripId:
            trip = db.execute(
                "SELECT id FROM trips WHERE id = ?", (tripId,)
            ).fetchone()
            if trip is None:
                raise HTTPException(status_code=404, detail="No existe el viaje indicado.")
            rows = db.execute(
                SELECT_PLACES + " WHERE p.tripId = ? ORDER BY p.tentativeDate ASC",
                (tripId,),
            ).fetchall()
        else:
            rows = db.execute(
                SELECT_PLACES + " ORDER BY p.tentativeDate ASC"
            ).fetchall()

    return [place_response(row) for row in rows]
