from fastapi import APIRouter
import httpx
from config import CAL_TXT_PATH, ICAL_URL
from icalendar import Calendar
from datetime import datetime, date
from contextlib import asynccontextmanager
import asyncio


# Startup
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

# Load Calendar for lifespan
async def load_calendar():
    """
    Refresh data/calendar.txt every 2 minutes.
    A failed refresh is logged and retried at the next turn.
    """
    while True:
        try:
            await get_calendar_from_google()
        except httpx.HTTPError as e:
            print(f"Calendar refresh failed: {e!r}")
        await asyncio.sleep(120)
        

# == GET ==
@router.get("/get_calendar")
async def get_calendar():
    """
    Read and Parse raw calendar data the returns them
    (empty list if calendar.txt hasn't been downloaded yet)
    """
    if not CAL_TXT_PATH.exists():
        return []

    with open (CAL_TXT_PATH, 'r', encoding="utf-8") as f:
        ical_content= f.read()
        events = parse_ical_events(ical_content)

    return events

async def get_calendar_from_google():
    """
    Get calendar as txt file and write everything in data/calendar.txt
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(ICAL_URL)
    response.raise_for_status()
    cal_data = response.text
    with open (CAL_TXT_PATH, 'w', encoding="utf-8") as f:
        f.write(cal_data)



def parse_ical_events(ical_content: str) -> list[dict]:
    """
    Parse ical calendar content and returns a list of dict
    """
    calendar = Calendar.from_ical(ical_content)
    events = []

    for component in calendar.walk():
        if component.name != "VEVENT":
            continue

        start = component.get("dtstart")
        end = component.get("dtend")

        events.append({
            "id": str(component.get("uid", "")),
            "title": str(component.get("summary", "")),
            "description": str(component.get("description", "")),
            "location": str(component.get("location", "")),
            "start": start.dt if start else None,
            "end": end.dt if end else None,
            "all_day": isinstance(start.dt, date)
                       and not isinstance(start.dt, datetime)
                       if start else False,
            "status": str(component.get("status", "")),
        })

    return events

