import sqlite3
from config import DB_PATH
from contextlib import contextmanager

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    # rows can be read by column name (row["name"]) and converted with dict(row)
    conn.row_factory = sqlite3.Row

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
    name TEXT NOT NULL);
    """

    habit_logs="""
    CREATE TABLE IF NOT EXISTS habit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY(habit_id) REFERENCES habits(id));
    """

    task="""
    CREATE TABLE IF NOT EXISTS task(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL);
    """

    with get_db() as conn:
        cur = conn.cursor()

        cur.execute(habits)
        cur.execute(habit_logs)
        cur.execute(task)

