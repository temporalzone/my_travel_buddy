import os
import sqlite3


def _resolve_db_name():
    # Use env var for production persistent disks (e.g. /var/data/travelbuddy.db on Render).
    env_path = os.getenv("DB_NAME") or os.getenv("DATABASE_PATH")
    if env_path:
        return env_path
    return os.path.join(os.path.dirname(__file__), "travelbuddy.db")


DB_NAME = _resolve_db_name()


def _ensure_db_dir(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

def get_db():
    _ensure_db_dir(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    def ensure_column(table, column, definition):
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in cols:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

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

    ensure_column("users", "age", "INTEGER")
    ensure_column("users", "gender", "TEXT")
    ensure_column("users", "profile_picture", "TEXT")
    ensure_column("users", "is_deleted", "INTEGER DEFAULT 0")
    ensure_column("users", "deleted_at", "TEXT")

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

    ensure_column("messages", "mentions", "TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS read_receipts (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            user_id    TEXT NOT NULL,
            read_at    TEXT NOT NULL,
            UNIQUE (message_id, user_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS message_reactions (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            user_id    TEXT NOT NULL,
            emoji      TEXT NOT NULL,
            reacted_at TEXT NOT NULL,
            UNIQUE (message_id, user_id, emoji)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS message_files (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            file_data  TEXT NOT NULL,
            file_type  TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS typing_status (
            user_id    TEXT NOT NULL,
            trip_id    TEXT NOT NULL,
            typing_at  TEXT NOT NULL,
            PRIMARY KEY (user_id, trip_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_otps (
            id         TEXT PRIMARY KEY,
            email      TEXT NOT NULL,
            otp_code   TEXT NOT NULL,
            payload    TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
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