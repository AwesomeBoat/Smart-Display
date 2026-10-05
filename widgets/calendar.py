import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, date, timedelta

import httpx
import recurring_ical_events
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from icalendar import Calendar

from config import CALENDARS_DIR
from data.db import get_db
from profiles.profile import find_active_profile


# === HELPERS ===

def get_calendar_path(profile_id: int):
    """Return the calendar file path of the given profile"""
    return CALENDARS_DIR / f"{profile_id}.txt"


# used by the display stream and the debug route
# read the local file only, the download is done by load_calendar
def fetch_events(profile_id: int) -> list[dict]:
    """Return the events of a given profile (empty list if not downloaded yet)"""
    calendar_path = get_calendar_path(profile_id)
    if not calendar_path.exists():
        return []

    with open(calendar_path, 'r', encoding="utf-8") as f:
        ical_content = f.read()
    # a broken file must not kill the stream, show nothing until next download
    try:
        return parse_ical_events(ical_content)
    except ValueError as e:
        print(f"Calendar of profile {profile_id} can't be parsed: {e!r}")
        return []


# === DOWNLOAD (background task) ===

@asynccontextmanager
async def lifespan(app):
    # keep a reference to the task, else Python may garbage-collect it
    refresh_task = asyncio.create_task(load_calendar())
    yield
    refresh_task.cancel()


router = APIRouter(
    prefix="/calendar",
    tags=["Calendar"],
    lifespan=lifespan
)


async def load_calendar():
    """
    Refresh data/calendars/{id}.txt of every profile with an ical_url every 2 minutes.
    A failed refresh is logged and retried at the next turn.
    """
    while True:
        # get all profile urls, then close the db before downloading
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, ical_url FROM profile WHERE ical_url IS NOT NULL AND ical_url != ''")
            profiles = cur.fetchall()
        # one try per profile so a broken url doesn't block the others
        for profile in profiles:
            try:
                await get_calendar_from_google(profile["id"], profile["ical_url"])
            except httpx.HTTPError as e:
                print(f"Calendar from profile {profile['id']} refresh failed: {e!r}")
        await asyncio.sleep(120)


async def get_calendar_from_google(profile_id: int, ical_url: str):
    """Download a calendar and write all the events in data/calendars/{profile_id}.txt"""
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(ical_url)
    response.raise_for_status()
    with open(get_calendar_path(profile_id), 'w', encoding="utf-8") as f:
        f.write(response.text)


# === PARSE ===

# only events from today to X days later are sent to the display
DAYS_AHEAD = 30


def sort_key(value) -> datetime:
    """Make dates comparable: all day (date), local (naive) and utc (aware) datetimes"""
    if not isinstance(value, datetime):
        value = datetime(value.year, value.month, value.day)
    # naive = local time, give it the local timezone
    return value.astimezone()


def parse_ical_events(ical_content: str) -> list[dict]:
    """Parse ical calendar content and return the events of the next DAYS_AHEAD days, sorted"""
    calendar = Calendar.from_ical(ical_content)
    today = date.today()
    # recurring_ical_events unfolds repeated events (RRULE: every monday...)
    # walk() would only give their first date, often in the past
    occurrences = recurring_ical_events.of(calendar).between(today, today + timedelta(days=DAYS_AHEAD))
    occurrences = sorted(occurrences, key=lambda component: sort_key(component.get("dtstart").dt))
    events = []

    for component in occurrences:
        start = component.get("dtstart")
        end = component.get("dtend")

        events.append({
            "id": str(component.get("uid", "")),
            "title": str(component.get("summary", "")),
            "description": str(component.get("description", "")),
            "location": str(component.get("location", "")),
            # isoformat: dates as text, so json.dumps works and JS can read them
            "start": start.dt.isoformat() if start else None,
            "end": end.dt.isoformat() if end else None,
            "all_day": isinstance(start.dt, date)
                       and not isinstance(start.dt, datetime)
                       if start else False,
            "status": str(component.get("status", "")),
        })

    return events


# === SSE ===

@router.get("/get_curr_calendar")
async def get_curr_calendar():
    """Stream the active profile events to the display (script.js)"""
    return StreamingResponse(media_type="text/event-stream", content=get_calendar_data())


async def get_calendar_data():
    """Every 5 seconds, send the events of the active profile"""
    while True:
        # check active profile at each loop so display follows profile switch
        with get_db() as conn:
            profile_id = find_active_profile(conn)
        events = json.dumps(fetch_events(profile_id))
        yield f"data: {events}\n\n"
        # 5s instead of 1s: parsing ical every second is heavy for the Pi
        # sleep after yield so the display gets the calendar right away
        await asyncio.sleep(5)


# === GET ===

@router.get("/get_calendar/{profile_id}")
async def get_calendar(profile_id: int):
    """Return the events of a given profile (debug)"""
    return fetch_events(profile_id)
