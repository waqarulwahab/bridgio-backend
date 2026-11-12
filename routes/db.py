import os
import sqlite3

_DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "bridgio.db"))


def _conn():
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                name TEXT,
                custom_name TEXT DEFAULT '',
                last_seen REAL,
                connected_at REAL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS rc_devices (
                id TEXT PRIMARY KEY,
                name TEXT,
                custom_name TEXT DEFAULT '',
                last_seen REAL,
                connected_at REAL
            )
        """)
        c.commit()


def load_devices() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT * FROM devices").fetchall()
    return {
        r["id"]: {
            "name": r["name"],
            "custom_name": r["custom_name"] or "",
            "online": False,
            "last_seen": r["last_seen"],
            "connected_at": r["connected_at"],
        }
        for r in rows
    }


def load_rc_devices() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT * FROM rc_devices").fetchall()
    return {
        r["id"]: {
            "name": r["name"],
            "custom_name": r["custom_name"] or "",
            "online": False,
            "last_seen": r["last_seen"],
            "connected_at": r["connected_at"],
        }
        for r in rows
    }


def upsert_device(did: str, data: dict):
    with _conn() as c:
        c.execute(
            """
            INSERT INTO devices (id, name, custom_name, last_seen, connected_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                custom_name=CASE WHEN excluded.custom_name != '' THEN excluded.custom_name ELSE devices.custom_name END,
                last_seen=excluded.last_seen,
                connected_at=excluded.connected_at
            """,
            (did, data["name"], data.get("custom_name", ""), data["last_seen"], data.get("connected_at", data["last_seen"])),
        )
        c.commit()


def upsert_rc_device(did: str, data: dict):
    with _conn() as c:
        c.execute(
            """
            INSERT INTO rc_devices (id, name, custom_name, last_seen, connected_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                custom_name=CASE WHEN excluded.custom_name != '' THEN excluded.custom_name ELSE rc_devices.custom_name END,
                last_seen=excluded.last_seen,
                connected_at=excluded.connected_at
            """,
            (did, data["name"], data.get("custom_name", ""), data["last_seen"], data.get("connected_at", data["last_seen"])),
        )
        c.commit()


def rename_device_db(did: str, custom_name: str):
    with _conn() as c:
        c.execute("UPDATE devices SET custom_name=? WHERE id=?", (custom_name, did))
        c.commit()


def delete_device_db(did: str):
    with _conn() as c:
        c.execute("DELETE FROM devices WHERE id=?", (did,))
        c.commit()


def db_path() -> str:
    return _DB_PATH
