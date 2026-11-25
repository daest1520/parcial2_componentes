import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "data" / "viajes.db")))
if not DB_PATH.is_absolute():
    DB_PATH = BASE_DIR / DB_PATH
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    from app.categories import INITIAL_CATEGORIES

    with get_connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL CHECK(length(name) <= 100),
            destination TEXT NOT NULL CHECK(length(destination) <= 120),
            startDate TEXT NOT NULL,
            endDate TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            CHECK(endDate >= startDate)
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE CHECK(length(name) <= 80),
            description TEXT NOT NULL CHECK(length(description) <= 250)
        );

        CREATE TABLE IF NOT EXISTS places (
            id TEXT PRIMARY KEY,
            tripId TEXT NOT NULL,
            name TEXT NOT NULL CHECK(length(name) <= 120),
            description TEXT NOT NULL CHECK(length(description) <= 1000),
            city TEXT NOT NULL CHECK(length(city) <= 100),
            categoryId INTEGER NOT NULL,
            tentativeDate TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL,
            FOREIGN KEY (tripId) REFERENCES trips(id) ON DELETE CASCADE,
            FOREIGN KEY (categoryId) REFERENCES categories(id)
        );

        CREATE INDEX IF NOT EXISTS idx_places_trip_date
        ON places(tripId, tentativeDate);
        """)
        for name, description in INITIAL_CATEGORIES:
            db.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (name, description),
            )
