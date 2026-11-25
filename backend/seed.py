from app.database import initialize_database, get_connection, DB_PATH
from app.utils import new_id, now_iso

initialize_database()

with get_connection() as db:
    db.execute("DELETE FROM places")
    db.execute("DELETE FROM trips")

    timestamp = now_iso()
    trip_id = new_id()
    db.execute(
        """INSERT INTO trips
        (id, name, destination, startDate, endDate, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (trip_id, "Europa 2026", "Italia", "2026-06-10", "2026-06-20", timestamp, timestamp),
    )

    examples = [
        ("Coliseo Romano", "Anfiteatro romano, uno de los principales atractivos de Roma.", "Roma", "Histórico", "2026-06-12"),
        ("Fontana di Trevi", "Fuente monumental ubicada en el centro de Roma.", "Roma", "Histórico", "2026-06-13"),
        ("Vaticano", "Lugar de interés histórico, artístico y religioso.", "Ciudad del Vaticano", "Religioso", "2026-06-15"),
    ]

    for name, description, city, category_name, tentative_date in examples:
        category = db.execute(
            "SELECT id FROM categories WHERE name = ?", (category_name,)
        ).fetchone()
        db.execute(
            """INSERT INTO places
            (id, tripId, name, description, city, categoryId, tentativeDate, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (new_id(), trip_id, name, description, city, category["id"], tentative_date, timestamp, timestamp),
        )

print("Datos de demostración creados correctamente.")
print("ID del viaje:", trip_id)
print("Archivo SQLite:", DB_PATH)
