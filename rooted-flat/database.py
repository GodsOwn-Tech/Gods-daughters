"""
database.py — everything to do with talking to database.db (SQLite).

SQLite stores the whole database in one file (database.db) that gets
created automatically the first time you run the app. You can open it
directly with any SQLite viewer (e.g. "DB Browser for SQLite") to see
exactly what's stored — handy for debugging.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["title"]
    return conn


def init_db():
    """Creates all tables if they don't already exist. Safe to call every
    time the app starts."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            handle TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            restricted INTEGER NOT NULL DEFAULT 0
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bible_studies (
            id TEXT PRIMARY KEY,
            week INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            sessions INTEGER NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id TEXT PRIMARY KEY,
            study_id TEXT NOT NULL,
            session_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            scripture_ref TEXT NOT NULL,
            questions TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_help (
            id TEXT PRIMARY KEY,
            struggle TEXT NOT NULL,
            title TEXT NOT NULL,
            excerpt TEXT NOT NULL
        )
    """)

    # Tap-an-emoji comfort feature on the Mood Help page. "messages" and
    # "verses" hold a few lines each, one per line — the frontend picks
    # one message at random and shows all verses as tappable chips.
    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_emojis (
            id TEXT PRIMARY KEY,
            emoji TEXT NOT NULL,
            label TEXT NOT NULL,
            messages TEXT NOT NULL,
            verses TEXT NOT NULL DEFAULT ''
        )
    """)

    # Private journal entries on the Mood Help page.
    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_journal (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            emoji TEXT NOT NULL,
            label TEXT NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prayer_wall (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            handle TEXT NOT NULL,
            content TEXT NOT NULL,
            anonymous INTEGER NOT NULL DEFAULT 0,
            hidden INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS prayer_reactions (
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            PRIMARY KEY (post_id, user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS gist (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            handle TEXT NOT NULL,
            content TEXT NOT NULL,
            hidden INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            tagged_handles TEXT NOT NULL DEFAULT ''
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS gist_reactions (
            message_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            reaction TEXT NOT NULL,
            PRIMARY KEY (message_id, user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            board TEXT NOT NULL,
            post_id TEXT NOT NULL,
            reason TEXT NOT NULL,
            reported_by TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id TEXT PRIMARY KEY,
            requester_id TEXT NOT NULL,
            addressee_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            code TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Bible study groups — lets 2+ friends work through a study together
    # and see each other's progress.
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_groups (
            id TEXT PRIMARY KEY,
            study_id TEXT NOT NULL,
            name TEXT NOT NULL,
            creator_id TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_group_members (
            group_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            handle TEXT NOT NULL,
            PRIMARY KEY (group_id, user_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS study_group_progress (
            group_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            PRIMARY KEY (group_id, session_id, user_id)
        )
    """)

    # Verse of the day — which one shows is picked deterministically from
    # today's date (see main.py), so it's the same for everyone all day.
    c.execute("""
        CREATE TABLE IF NOT EXISTS votd_verses (
            id TEXT PRIMARY KEY,
            reference TEXT NOT NULL
        )
    """)

    # Six floating affirmations shown at the top of the Devotionals page.
    c.execute("""
        CREATE TABLE IF NOT EXISTS affirmations (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL
        )
    """)

    # Notifications — likes/reactions, friend requests, prayers on your
    # posts, anything that needs the user's attention.
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    # Safe to re-run: adds columns to tables that might already exist from
    # an earlier version of database.db, without touching existing data.
    for stmt in [
        "ALTER TABLE gist ADD COLUMN tagged_handles TEXT NOT NULL DEFAULT ''",
        "ALTER TABLE mood_emojis ADD COLUMN verses TEXT NOT NULL DEFAULT ''",
    ]:
        try:
            c.execute(stmt)
        except sqlite3.OperationalError:
            pass  # column already exists

    conn.commit()
    conn.close()
