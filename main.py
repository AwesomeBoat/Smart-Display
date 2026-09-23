from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from datetime import datetime, date
import asyncio
import httpx
from dotenv import load_dotenv
import os
from typing import Annotated
import json
import sqlite3
from icalendar import Calendar
from contextlib import asynccontextmanager


# Startup
@asynccontextmanager
async def lifespan(app):
    while True:
        asyncio.create_task(get_calendar_from_google())
        await asyncio.sleep(60)
        yield
        pass

app = FastAPI(lifespan=lifespan)
load_dotenv()

# CONSTANTS FROM .ENV
LAT = os.getenv("LAT")
LON = os.getenv("LON")
ICAL_URL = os.getenv("ICAL_URL")

# SQLite con
con = sqlite3.connect("data/mirror.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS task(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at TEXT)")
con.close()


# API 
@app.get("/")
def health():
    return {"status": "ok"}



# Send actual time to front
@app.get("/get_time")
def get_time():
    return StreamingResponse(media_type="text/event-stream",content=hour())

# return the html index
@app.get("/mirror_dashboard")
def get_mirror_dashboard():
    return FileResponse("front/index.html")


@app.get("/script.js")
def get_js_file():
    return FileResponse("front/script.js")


@app.get("/get_curr_weather_data")
def get_curr_weather_data():
    return StreamingResponse(media_type="text/event-stream",content=get_curr_weather())

# TO-DO route
@app.post("/add_task")
def add_task(task : Annotated[str, Form()]):
    con = sqlite3.connect("data/mirror.db")
    cur = con.cursor()
    now = datetime.now().strftime("%H:%M:%S")
    command = f"INSERT INTO task (name, created_at) VALUES (?, ?)"
    cur.execute(command, (task,now))
    con.commit()
    con.close()
    return RedirectResponse("/mirror_dashboard", status_code=303)


@app.get("/get_curr_todo")
def get_curr_todo():
    return StreamingResponse(media_type="text/event-stream", content=get_todo())


async def get_todo():
    while True:
        await asyncio.sleep(1)
        con = sqlite3.connect("data/mirror.db")
        cur = con.cursor()
        command = "SELECT * FROM task"
        tasks = json.dumps(cur.execute(command).fetchall())
        con.close()
        yield f"data: {tasks}\n\n"

# Async func for /hour route
async def hour():
    while True:
        await asyncio.sleep(1)
        now = datetime.now().strftime("%H:%M:%S")
        yield f"data: {now}\n\n"


# async func for weather api
async def get_curr_weather():
    while True:
        await asyncio.sleep(5)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true" 
        response = httpx.get(url).json()
        weather_data = response['current_weather']
        data = {"temperature:":weather_data['temperature'],
                "windspeed":weather_data['windspeed']}
        yield f"data: {data['temperature:']}°C | Wind {data['windspeed']}\n\n"


# func for calendar

@app.get("/get_calendar")
def get_calendar():
    calendar_data_path = "data/calendar.txt"
    with open (calendar_data_path, 'r', encoding="utf-8") as f:
        ical_content= f.read()

        events = parse_ical_events(ical_content)

    return events

def get_calendar_from_google():
    """
    Get calendar as txt file and write everything in data/calendar.txt
    """
    response = httpx.get(ICAL_URL)
    cal_data = response.text
    with open ("data/calendar.txt", 'w') as f:
        f.writelines(cal_data)



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

