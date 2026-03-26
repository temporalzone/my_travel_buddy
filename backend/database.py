import sqlite3

DB_NAME = "travelbuddy.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            location    TEXT DEFAULT 'Earth',
            bio         TEXT DEFAULT 'New traveler!',
            interests   TEXT DEFAULT '',
            joined_at   TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id          TEXT PRIMARY KEY,
            title       TEXT NOT NULL,
            destination TEXT NOT NULL,
            emoji       TEXT DEFAULT '🌍',
            dates       TEXT NOT NULL,
            duration    TEXT DEFAULT 'TBD',
            budget      TEXT DEFAULT 'Mid-range',
            style       TEXT DEFAULT 'Adventure',
            seats       INTEGER DEFAULT 3,
            total_seats INTEGER DEFAULT 4,
            tags        TEXT DEFAULT '',
            host_id     TEXT NOT NULL,
            created_at  TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip_members (
            trip_id   TEXT NOT NULL,
            user_id   TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            PRIMARY KEY (trip_id, user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id       TEXT PRIMARY KEY,
            trip_id  TEXT NOT NULL,
            user_id  TEXT NOT NULL,
            text     TEXT NOT NULL,
            sent_at  TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS join_requests (
            id           TEXT PRIMARY KEY,
            trip_id      TEXT NOT NULL,
            requester_id TEXT NOT NULL,
            status       TEXT NOT NULL DEFAULT 'pending',
            requested_at TEXT NOT NULL,
            reviewed_at  TEXT,
            UNIQUE (trip_id, requester_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database ready!")