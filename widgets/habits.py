from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Annotated
import asyncio
import json
from data.db import get_db

router = APIRouter(
    prefix="/habits",
    tags=["Habits"]
)


def check_habit_exists(conn, habit_id: int):
    """Raise a 404 if no habit has this id"""
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM habits WHERE id = ?", (habit_id,))
    if cur.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail="Habit not found"
        )


# === HABITS ===
@router.get("/get_habits")
async def get_habits():
    """Return all habits"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits")
        return [dict(row) for row in cur.fetchall()]


@router.get("/get_habit/{habit_id}")
async def get_habit(habit_id: int):
    """Return one habit as a dict (id, name)"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        data = cur.fetchone()
        if data is None:
            raise HTTPException(
                status_code=404,
                detail="Habit not found"
            )
        return dict(data)


@router.post("/add_habit", status_code=201)
async def add_habit(name: Annotated[str, Form()]):
    """Add a habit to the habits table and return it"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO habits (name) VALUES (?)", (name,))
        return {"id": cur.lastrowid, "name": name}


@router.delete("/delete_habit/{habit_id}")
async def delete_habit(habit_id: int):
    """Delete a habit and its logs"""
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        conn.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
        conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    return {
        "success": True,
        "message": f"Habit {habit_id} deleted"
    }


# === HABIT LOGS ===
@router.post("/add_log/{habit_id}")
async def add_habit_log(habit_id: int):
    """
    Log today for a habit (only one log per day).
    "created" is False if today was already logged.
    """
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        today = datetime.now().date().isoformat()
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM habit_logs WHERE habit_id = ? AND date = ?",
            (habit_id, today)
        )
        created = cur.fetchone() is None
        if created:
            cur.execute(
                "INSERT INTO habit_logs (habit_id, date) VALUES (?, ?)",
                (habit_id, today)
            )
        return {"habit_id": habit_id, "date": today, "created": created}


@router.get("/get_logs/{habit_id}")
async def get_habit_logs(habit_id: int):
    """Return all logs of a habit"""
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        cur = conn.cursor()
        cur.execute("SELECT * FROM habit_logs WHERE habit_id = ?", (habit_id,))
        return [dict(row) for row in cur.fetchall()]


@router.delete("/delete_today_log/{habit_id}")
async def delete_today_log(habit_id: int):
    """Remove today's log of a habit if accidentally checked"""
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        today = datetime.now().date().isoformat()
        conn.execute(
            "DELETE FROM habit_logs WHERE habit_id = ? AND date = ?",
            (habit_id, today)
        )
    return {
        "success": True,
        "message": f"Today's log of habit {habit_id} deleted"
    }


# === STREAK ===
def streak(dates: list[datetime]):
    """Count streak days ending today or yesterday"""
    if not dates:
        return 0

    # convert into date objects and get rid of duplicates
    unique_dates = {d.date() if isinstance(d, datetime) else d for d in dates}

    # Sort dates
    ordered_dates = sorted(list(unique_dates))

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # if the last day isn't today or yesterday, no streak
    last_date = ordered_dates[-1]
    if last_date != today and last_date != yesterday:
        return 0

    # Count streak
    streak_count = 1

    for i in range(len(ordered_dates) - 1, 0, -1):
        if ordered_dates[i] - ordered_dates[i-1] == timedelta(days=1):
            streak_count += 1
        else:
            break
    return streak_count


def habit_streak(conn, habit_id: int):
    """Read the logs of a habit in the db and return its current streak"""
    cur = conn.cursor()
    cur.execute("SELECT date FROM habit_logs WHERE habit_id = ?", (habit_id,))
    rows = cur.fetchall()  # [{"date": "2026-10-04"}, ...]

    dates = [datetime.strptime(row["date"], "%Y-%m-%d").date() for row in rows]
    return streak(dates)


@router.get("/get_streak/{habit_id}")
async def get_habit_streak(habit_id: int):
    """Return the current streak of a habit"""
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        return {"habit_id": habit_id, "streak": habit_streak(conn, habit_id)}


# === SSE ===
@router.get("/get_curr_habits")
async def get_curr_habits():
    """
    Streaming Response to js script from get_habits_data function
    """
    return StreamingResponse(media_type="text/event-stream", content=get_habits_data())


async def get_habits_data():
    """
    yield all habits with their current streak every sec
    """
    while True:
        await asyncio.sleep(1)
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM habits")
            habits = [
                {"id": row["id"], "name": row["name"], "streak": habit_streak(conn, row["id"])}
                for row in cur.fetchall()
            ]
        yield f"data: {json.dumps(habits)}\n\n"
