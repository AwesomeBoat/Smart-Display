from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
from typing import Annotated
import asyncio
import json
from data.db import get_db
from profiles.profile import find_active_profile, check_if_profile_exists

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
    """Return all habits, every profile included (debug)"""
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


@router.post("/add_habit/{profile_id}", status_code=201)
async def add_habit(name: Annotated[str, Form()], profile_id: int):
    """Add a habit to a profile and return it"""
    with get_db() as conn:
        # check profile exists, else the foreign key would raise a 500
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        cur = conn.cursor()
        cur.execute("INSERT INTO habits (name, profile_id) VALUES (?, ?)", (name, profile_id))
        return {"id": cur.lastrowid, "name": name, "profile_id": profile_id}


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


# used by both streams (display + phone)
# get the profile_id from the caller, don't check active profile here
def fetch_habits(conn, profile_id: int) -> list[dict]:
    """Return all habits of a given profile with their current streak"""
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM habits WHERE profile_id = ?", (profile_id,))
    return [
        {"id": row["id"], "name": row["name"], "streak": habit_streak(conn, row["id"])}
        for row in cur.fetchall()
    ]


@router.get("/get_streak/{habit_id}")
async def get_habit_streak(habit_id: int):
    """Return the current streak of a habit"""
    with get_db() as conn:
        check_habit_exists(conn, habit_id)
        return {"habit_id": habit_id, "streak": habit_streak(conn, habit_id)}


# === SSE ===
# same as todo : display follows the active profile, phones their own profile

# --- Display ---

@router.get("/get_curr_habits")
async def get_curr_habits():
    """Stream the active profile habits to the display (script.js)"""
    return StreamingResponse(media_type="text/event-stream", content=get_habits_data())


async def get_habits_data():
    """Every second, send the habits of the active profile with their streak"""
    while True:
        await asyncio.sleep(1)
        # check active profile at each loop so display follows profile switch
        with get_db() as conn:
            habits = json.dumps(fetch_habits(conn, find_active_profile(conn)))
        yield f"data: {habits}\n\n"


# --- Phone ---

@router.get("/stream_habits/{profile_id}")
async def stream_profile_habits(profile_id: int):
    """Stream the habits of the given profile (phone)"""
    # check profile b4 streaming, once started 200 is already sent so no 404 possible
    with get_db() as conn:
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
    return StreamingResponse(media_type="text/event-stream", content=stream_habit_gen(profile_id))


async def stream_habit_gen(profile_id: int):
    """Every second, send the habits of the given profile with their streak"""
    # same as get_habits_data but profile_id comes from the phone
    while True:
        await asyncio.sleep(1)
        with get_db() as conn:
            habits = json.dumps(fetch_habits(conn, profile_id))
        yield f"data: {habits}\n\n"
