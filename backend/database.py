import os
import sqlite3
import importlib
import socket
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)


def _load_postgres_driver():
    psycopg2_error = None
    try:
        psycopg2 = importlib.import_module("psycopg2")
        dict_cursor = importlib.import_module("psycopg2.extras").RealDictCursor
        return "psycopg2", psycopg2, dict_cursor
    except Exception as e:
        psycopg2_error = str(e)

    try:
        psycopg = importlib.import_module("psycopg")
        dict_row = importlib.import_module("psycopg.rows").dict_row
        return "psycopg3", psycopg, dict_row
    except Exception as e:
        raise RuntimeError(
            "DATABASE_URL is set but no PostgreSQL driver could be loaded. "
            f"psycopg2 error: {psycopg2_error}; psycopg error: {e}"
        )


def _resolve_db_name():
    # Use env var for production persistent disks (e.g. /var/data/travelbuddy.db on Render).
    env_path = os.getenv("DB_NAME") or os.getenv("DATABASE_PATH")
    if env_path:
        return env_path
    return os.path.join(os.path.dirname(__file__), "travelbuddy.db")


DB_NAME = _resolve_db_name()


def _inject_hostaddr_ipv4(db_url):
    """Return a DATABASE_URL with hostaddr=<ipv4> for libpq IPv4 fallback."""
    parsed = urlparse(db_url)
    host = parsed.hostname
    port = parsed.port or 5432
    if not host:
        return None

    query_items = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "hostaddr" in query_items:
        return db_url

    try:
        infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
    except Exception:
        return None

    if not infos:
        return None

    ipv4 = infos[0][4][0]
    query_items["hostaddr"] = ipv4
    query_items.setdefault("sslmode", "require")

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(query_items),
            parsed.fragment,
        )
    )


def _convert_sql(sql):
    # Convert sqlite-style placeholders to postgres placeholders.
    return sql.replace("?", "%s")


class PgCompatConn:
    def __init__(self, raw_conn, driver_kind, row_helper):
        self._raw_conn = raw_conn
        self._driver_kind = driver_kind
        self._row_helper = row_helper

    def execute(self, sql, params=()):
        if self._driver_kind == "psycopg2":
            cur = self._raw_conn.cursor(cursor_factory=self._row_helper)
        else:
            cur = self._raw_conn.cursor(row_factory=self._row_helper)
        cur.execute(_convert_sql(sql), params)
        return cur

    def commit(self):
        self._raw_conn.commit()

    def close(self):
        self._raw_conn.close()


def _ensure_db_dir(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

def get_db():
    if USE_POSTGRES:
        driver_kind, driver_module, row_helper = _load_postgres_driver()
        try:
            return PgCompatConn(driver_module.connect(DATABASE_URL), driver_kind, row_helper)
        except Exception as e:
            err = str(e)
            # Supabase direct host can resolve to IPv6 first in some environments.
            # Retry once with hostaddr=<ipv4> so connection uses IPv4 transport.
            if "Network is unreachable" in err or "connection is bad" in err:
                ipv4_url = _inject_hostaddr_ipv4(DATABASE_URL)
                if ipv4_url and ipv4_url != DATABASE_URL:
                    return PgCompatConn(driver_module.connect(ipv4_url), driver_kind, row_helper)
            raise

    _ensure_db_dir(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()

    def ensure_column(table, column, definition):
        if USE_POSTGRES:
            exists = conn.execute(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = ? AND column_name = ?
                """,
                (table, column),
            ).fetchone()
            if not exists:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {definition}")
        else:
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
            if column not in cols:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    conn.execute("""
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

    conn.execute("""
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS trip_members (
            trip_id   TEXT NOT NULL,
            user_id   TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            PRIMARY KEY (trip_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id       TEXT PRIMARY KEY,
            trip_id  TEXT NOT NULL,
            user_id  TEXT NOT NULL,
            text     TEXT NOT NULL,
            sent_at  TEXT NOT NULL
        )
    """)

    ensure_column("messages", "mentions", "TEXT")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS read_receipts (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            user_id    TEXT NOT NULL,
            read_at    TEXT NOT NULL,
            UNIQUE (message_id, user_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_reactions (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            user_id    TEXT NOT NULL,
            emoji      TEXT NOT NULL,
            reacted_at TEXT NOT NULL,
            UNIQUE (message_id, user_id, emoji)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS message_files (
            id         TEXT PRIMARY KEY,
            message_id TEXT NOT NULL,
            file_name  TEXT NOT NULL,
            file_data  TEXT NOT NULL,
            file_type  TEXT NOT NULL,
            uploaded_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS typing_status (
            user_id    TEXT NOT NULL,
            trip_id    TEXT NOT NULL,
            typing_at  TEXT NOT NULL,
            PRIMARY KEY (user_id, trip_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS email_otps (
            id         TEXT PRIMARY KEY,
            email      TEXT NOT NULL,
            otp_code   TEXT NOT NULL,
            payload    TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
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