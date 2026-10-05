from fastapi import APIRouter, HTTPException, Form
from data.db import get_db
from typing import Annotated

router = APIRouter(
    prefix="/profile",
    tags=["Profiles"]
)

@router.get("/get_all_profiles")
def get_all_profiles() -> list[dict]:
    """Returns all profiles"""
    with get_db() as conn:
        cur = conn.cursor()
        command = "SELECT id, name, active FROM profile"
        cur.execute(command)
        profiles = cur.fetchall()
        return [dict(row) for row in profiles]


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
        cur.execute("SELECT id, name, active FROM profile WHERE id=?", (profile_id,))
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

