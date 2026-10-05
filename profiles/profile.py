import asyncio
import json
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import StreamingResponse

from data.db import get_db

router = APIRouter(
    prefix="/profile",
    tags=["Profiles"]
)

@router.get("/get_all_profiles")
def get_all_profiles() -> list[dict]:
    """Returns all profiles"""
    with get_db() as conn:
        cur = conn.cursor()
        command = "SELECT id, name, active, display_mode, theme FROM profile"
        cur.execute(command)
        profiles = cur.fetchall()
        return [dict(row) for row in profiles]


# === DISPLAY SETTINGS (mode + theme of the display) ===
# declared BEFORE "/{profile_id}", else FastAPI would read "get_curr_display" as an id

DisplayMode = Literal["jour", "semaine"]
Theme = Literal["glacier", "braise", "ivoire"]


@router.get("/get_curr_display")
async def get_curr_display():
    """Stream the display settings of the active profile to the display (display.js)"""
    return StreamingResponse(media_type="text/event-stream", content=get_display_data())


async def get_display_data():
    """Every second, send {"mode", "theme"} of the active profile"""
    while True:
        # check active profile at each loop so display follows profile switch
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT display_mode, theme FROM profile WHERE active = 1")
            row = cur.fetchone()
        settings = {"mode": row["display_mode"], "theme": row["theme"]}
        yield f"data: {json.dumps(settings)}\n\n"
        # sleep after yield so the display gets its settings right away
        await asyncio.sleep(1)


@router.patch("/set_display/{profile_id}")
def set_display(
    profile_id: int,
    display_mode: Annotated[DisplayMode, Form()],
    theme: Annotated[Theme, Form()],
):
    """Change the display mode and theme of a profile, return the profile"""
    # Literal: FastAPI answers 422 by itself if the value isn't in the list
    with get_db() as conn:
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        cur = conn.cursor()
        cur.execute(
            "UPDATE profile SET display_mode = ?, theme = ? WHERE id = ?",
            (display_mode, theme, profile_id)
        )
        cur.execute("SELECT id, name, active, display_mode, theme FROM profile WHERE id = ?", (profile_id,))
        return dict(cur.fetchone())


@router.get("/{profile_id}")
def get_profile_by_id(profile_id: int):
    """return specific profile infos"""
    with get_db() as conn:
            # check if id exists
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        cur = conn.cursor()
        cur.execute("SELECT id, name, active, display_mode, theme FROM profile WHERE id=?", (profile_id,))
        return dict(cur.fetchone())

@router.post("/create_profile")
def create_profile(name: Annotated[str, Form()], ical_url: Annotated[str | None, Form()] = None):
    """Create a profile in the db"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO profile (name, ical_url, active) VALUES (?,?,?)", (name, ical_url, 0))
        return {"id": cur.lastrowid, "name":name, "has_ical":bool(ical_url)}


@router.delete("/delete_profile/{profile_id}", status_code=204)
def delete_profile(profile_id: int):
    """Delete a profile and everything it owns(task, habits + logs)"""

    with get_db() as conn:

    # Check if profile exists
        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        cur = conn.cursor()

        # Check if profile is active
        cur.execute("SELECT active FROM profile WHERE id = ?", (profile_id,))
        if cur.fetchone()["active"]:
            raise HTTPException(
                status_code=409,
                detail="Can't delete the active profile, activate another one before"
            )
        # Delete habits, habit_logs and task b4 deleting the profile as they contain foreign keys
        # logs have no profile_id, find them through the profile's habits
        cur.execute("DELETE FROM habit_logs WHERE habit_id IN (SELECT id FROM habits WHERE profile_id = ?)", (profile_id,))
        cur.execute("DELETE FROM habits WHERE profile_id = ?",(profile_id,))
        cur.execute("DELETE FROM task WHERE profile_id = ?",(profile_id,))
        cur.execute("DELETE FROM profile WHERE id = ?", (profile_id,))
        




@router.patch("/set_active/{profile_id}")
def set_active(profile_id: int):
    """make a profile the only active, return it"""
    with get_db() as conn:
        cur = conn.cursor()

        if not check_if_profile_exists(conn, profile_id):
            raise HTTPException(
                status_code=404,
                detail= f"Error : could not find id {profile_id}"
            )
        if check_if_profile_active(conn, profile_id):
            cur.execute("SELECT id, name, active FROM profile WHERE id = ?", (profile_id,))
            return dict(cur.fetchone())
        
        
        # set inactive whoever is active
        cur.execute("UPDATE profile SET active = ? WHERE active = ? ", (0, 1))
        # set active the requested profile
        cur.execute("UPDATE profile SET active = ? WHERE id = ?", (1,profile_id))
        # return the active profile infos
        cur.execute("SELECT id, name, active FROM profile WHERE id = ?", (profile_id,))
        return dict(cur.fetchone())

def check_if_profile_exists(conn, profile_id: int):
    """Return True if profile exists"""
    cur = conn.cursor()
    cur.execute("SELECT id FROM profile WHERE id = ?", (profile_id,))
    if cur.fetchone() is None:
        return False
    return True


def check_if_profile_active(conn, profile_id: int):
        """Return True if profile is active"""
        cur = conn.cursor()
        cur.execute("SELECT active FROM profile where id = ?",(profile_id,))
        if cur.fetchone()["active"] == 0:
            return False
        return True

def find_active_profile(conn):
    """Return the id of the current active profile"""
    cur = conn.cursor()
    cur.execute("SELECT id FROM profile WHERE active = ?", (1,))
    return cur.fetchone()["id"]

