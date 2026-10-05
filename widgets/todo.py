import asyncio
import json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import StreamingResponse

from data.db import get_db
from profiles.profile import find_active_profile, check_if_profile_exists

router = APIRouter(
    prefix="/todo",
    tags=["Todo"]
)


# === HELPERS ===

# used by both streams (display + phone)
# get the profile_id from the caller, don't check active profile here
def fetch_tasks(conn, profile_id: int) -> list[dict]:
    """Return all tasks of a given profile as a list of dicts"""
    cur = conn.cursor()
    cur.execute("SELECT * FROM task WHERE profile_id = ?", (profile_id,))
    return [dict(row) for row in cur.fetchall()]


# === SSE ===
# route opens the stream, generator sends the data every second
# 2 streams : display (active profile) and phones (their own profile)

# --- Display ---

@router.get("/get_curr_todo")
async def get_curr_todo():
    """Stream the active profile tasks to the display (script.js)"""
    return StreamingResponse(media_type="text/event-stream", content=get_todo())


async def get_todo():
    """Every second, send the tasks of the active profile"""
    while True:
        await asyncio.sleep(1)
        # open db only for the query, not during sleep/yield (stream can stay open for days)
        with get_db() as conn:
            # check active profile at each loop so display follows profile switch
            tasks = json.dumps(fetch_tasks(conn, find_active_profile(conn)))
        # convert to json else JSON.parse fails in js
        yield f"data: {tasks}\n\n"


# --- Phone ---

@router.get("/stream_tasks/{profile_id}")
async def stream_profile_tasks(profile_id: int):
    """Stream the tasks of the given profile (phone)"""
    # check profile b4 streaming, once started 200 is already sent so no 404 possible
    with get_db() as conn:
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
    return StreamingResponse(media_type="text/event-stream", content=stream_task_gen(profile_id))


async def stream_task_gen(profile_id: int):
    """Every second, send the tasks of the given profile"""
    # same as get_todo but profile_id comes from the phone
    while True:
        await asyncio.sleep(1)
        with get_db() as conn:
            tasks = json.dumps(fetch_tasks(conn, profile_id))
        yield f"data: {tasks}\n\n"

# === GET ===

@router.get("/get_all_tasks")
async def get_all_tasks():
    """Return all tasks, every profile included (debug)"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM task")
        return [dict(row) for row in cur.fetchall()]


# === POST / PATCH / DELETE ===

@router.post("/add_task/{profile_id}", status_code=201)
async def add_task(task: Annotated[str, Form()], profile_id: int):
    """Add a task to a profile and return it"""
    with get_db() as conn:
        # check profile exists, else the foreign key would raise a 500
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        cur = conn.cursor()
        now = datetime.now().strftime("%H:%M:%S")
        command = "INSERT INTO task (name, profile_id, created_at) VALUES (?, ?, ?)"
        cur.execute(command, (task, profile_id, now))
        return {"id": cur.lastrowid, "name": task, "profile_id": profile_id, "created_at": now, "done": 0}


@router.patch("/toggle_task/{id}")
async def toggle_task(id: int):
    """Check or uncheck a task (done 0 <-> 1) and return it"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM task WHERE id = ?", (id,))
        task = cur.fetchone()
        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        # flip done
        new_done = 0 if task["done"] else 1
        cur.execute("UPDATE task SET done = ? WHERE id = ?", (new_done, id))
        return {**dict(task), "done": new_done}


@router.delete("/delete_task/{id}")
async def delete_task(id: int):
    """Delete a task by its id"""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM task WHERE id = ?", (id,))
        # nothing deleted = id doesn't exist
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
    return {
        "success": True,
        "message": f"Task {id} deleted"
    }
