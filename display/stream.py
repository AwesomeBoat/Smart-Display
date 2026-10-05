"""
One SSE stream for the whole display.

Why: a browser keeps at most 6 connections open to the same server (HTTP/1.1).
With one stream per widget, the display alone used all 6, so any other stream
(the calendar, or the phone opened in the same browser) waited forever.

How: each widget keeps its own generator, unchanged. This file runs them all
at once and merges their messages into ONE stream, each message tagged with
the name of its widget, so the front knows who it is for:

    event: clock
    data: 16:24:37

Metaphor: one radio station, several programmes, each announced by its name.
"""
import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from profiles import profile
from widgets import calendar, clock, habits, todo, weather

router = APIRouter(
    prefix="/display",
    tags=["Display"]
)

# event name (read by front/js/display.js) -> generator function of the widget
SOURCES = {
    "settings": profile.get_display_data,
    "clock": clock.hour,
    "weather": weather.get_curr_weather,
    "todo": todo.get_todo,
    "habits": habits.get_habits_data,
    "calendar": calendar.get_calendar_data,
}


@router.get("/stream")
async def display_stream():
    """Stream every widget of the display through one connection"""
    return StreamingResponse(media_type="text/event-stream", content=merge_sources())


async def forward(name: str, generator, queue: asyncio.Queue):
    """Read one widget generator and put its messages, tagged with the widget name, in the queue"""
    try:
        async for message in generator:
            # message is already "data: ...\n\n": add the event name in front
            await queue.put(f"event: {name}\n{message}")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        # a broken widget must not kill the others, it stays silent until the display reconnects
        print(f"Display stream: widget {name} stopped: {e!r}")


async def merge_sources():
    """Run every widget generator at the same time and yield their messages as they come"""
    queue = asyncio.Queue()
    tasks = [
        asyncio.create_task(forward(name, make_generator(), queue))
        for name, make_generator in SOURCES.items()
    ]
    try:
        while True:
            yield await queue.get()
    finally:
        # the display disconnected (or reloaded): stop every widget loop
        for task in tasks:
            task.cancel()
