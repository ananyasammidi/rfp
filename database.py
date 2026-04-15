"""
SQLite schema
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "rfp.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS menus (
            id          TEXT PRIMARY KEY,
            url         TEXT NOT NULL,
            restaurant  TEXT NOT NULL,
            scraped_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS items (
            id          TEXT PRIMARY KEY,
            menu_id     TEXT NOT NULL REFERENCES menus(id),
            name        TEXT NOT NULL,
            description TEXT,
            price       TEXT,
            category    TEXT
        );

        CREATE TABLE IF NOT EXISTS ingredients (
            id              TEXT PRIMARY KEY,
            dish_id         TEXT NOT NULL REFERENCES items(id),
            menu_id         TEXT NOT NULL REFERENCES menus(id),
            raw_name        TEXT NOT NULL,
            normalized_name TEXT NOT NULL,
            quantity        REAL,
            unit            TEXT
        );

        CREATE TABLE IF NOT EXISTS pricing (
            id              TEXT PRIMARY KEY,
            menu_id         TEXT NOT NULL REFERENCES menus(id),
            normalized_name TEXT NOT NULL,
            display_price   REAL,
            display_unit    TEXT,
            trend           TEXT,
            usda_category   TEXT,
            usda_description TEXT,
            source          TEXT DEFAULT 'USDA ERS Market Estimate (Q4 2024)'
        );

        CREATE TABLE IF NOT EXISTS distributors (
            id          TEXT PRIMARY KEY,
            menu_id     TEXT NOT NULL REFERENCES menus(id),
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            phone       TEXT,
            address     TEXT
        );

        CREATE TABLE IF NOT EXISTS emails (
            id              TEXT PRIMARY KEY,
            menu_id         TEXT NOT NULL REFERENCES menus(id),
            distributor_id  TEXT NOT NULL REFERENCES distributors(id),
            to_address      TEXT NOT NULL,
            subject         TEXT NOT NULL,
            body            TEXT NOT NULL,
            status          TEXT DEFAULT 'pending',
            sent_at         TEXT,
            error_msg       TEXT
        );

        CREATE TABLE IF NOT EXISTS pipeline_logs (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_id TEXT NOT NULL,
            step    TEXT NOT NULL,
            status  TEXT NOT NULL,
            message TEXT,
            ts      TEXT DEFAULT (datetime('now'))
        );
        """)


def fetchall(conn, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def fetchone(conn, sql: str, params: tuple = ()) -> dict | None:
    row = conn.execute(sql, params).fetchone()
    return dict(row) if row else None
