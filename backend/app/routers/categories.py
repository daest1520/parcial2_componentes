from fastapi import APIRouter
from app.database import get_connection

router = APIRouter(prefix="/api/categories", tags=["Categorías"])


@router.get("", summary="Consultar las categorías disponibles")
def get_categories():
    with get_connection() as db:
        rows = db.execute(
            "SELECT id, name, description FROM categories ORDER BY name ASC"
        ).fetchall()
    return [dict(row) for row in rows]
