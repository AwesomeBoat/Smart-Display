from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from datetime import datetime
import asyncio
import httpx
from dotenv import load_dotenv
import os
from typing import Annotated
import json
import sqlite3

app = FastAPI()
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
def get_calendar():
    response = httpx.get(ICAL_URL)
    cal_data = response.text
    with open ("data/calendar.txt", 'w') as f:
        f.writelines(cal_data)



def get_upcoming_events(ical_text):
    events = []
    with open (ical_text, 'r') as f:
    
        in_event = False
        outdated = True

        for line in f.readlines():
            
            line = line.strip()
            print(line)
            if line == "BEGIN:VEVENT":
                in_event = True
                new_event = {}

            elif line == "END:VEVENT": # APPEND THE EVENT TO THE LIST IF NOT OUTDATED
                # add event only if date >= today
                if not outdated:
                    events.append(new_event)
                in_event = False
                outdated = True

            if in_event: # ADD KEYS AND VALUES FOR THE EVENT
                if line.startswith("SUMMARY:") or line.startswith("DTSTART:"):
                    key, value = line.split(":", maxsplit=1)
                    new_event[key]=value

                    # Check if date value is >= today
                if line.startswith("DTSTART") or line.startswith("DTEND"):
                    event_date = line.split(":")[-1][:-1]  #[-1] bcs [0] is DTSTART / DTEND | [:-1] get rid of the "z" at the end of the date value
                    event_date_py = datetime.strptime(event_date, "%Y%m%dT%H%M%S") # Transform the str into a date type
                    now = datetime.now()
                    if event_date_py >= now: # Compare event date and today
                        outdated = False
            else:
                continue

    return events
        
                
print(get_upcoming_events("data/calendar.txt"))