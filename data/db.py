import sqlite3
from config import DB_PATH
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    # rows can be read by column name (row["name"]) and converted with dict(row)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
        raise e
    finally:
        conn.close()
    
    

def init_db():
    """Create tables if doesn't exists"""

    habits="""
    CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    profile_id INTEGER NOT NULL,
    FOREIGN KEY(profile_id) REFERENCES profile(id));
    """

    habit_logs="""
    CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    profile_id INTEGER NOT NULL,
    FOREIGN KEY(habit_id) REFERENCES habits(id),
    FOREIGN KEY(profile_id) REFERENCES profile(id));
    """

    task="""
    CREATE TABLE IF NOT EXISTS task(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    profile_id INTEGER NOT NULL,
    done INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(profile_id) REFERENCES profile(id));
    """

    profile="""
    CREATE TABLE IF NOT EXISTS profile(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ical_url TEXT,
    active INTEGER NOT NULL DEFAULT 0);
    """

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(profile)
        cur.execute(habits)
        cur.execute(habit_logs)
        cur.execute(task)

        # Create a default profile if doesn't exists
        cur.execute("SELECT COUNT(*) AS n FROM profile")
        if cur.fetchone()["n"] == 0:
            cur.execute("INSERT INTO profile (name, active) VALUES (?,?)", ("Default",1))


if __name__ == "__main__":
    init_db()
