from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse
from datetime import datetime
import asyncio
import httpx
from dotenv import load_dotenv
import os
from typing import Annotated
import json


app = FastAPI()
load_dotenv()

LAT = os.getenv("LAT")
LON = os.getenv("LON")

todos = []

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/get_time")
def get_time():
    return StreamingResponse(media_type="text/event-stream",content=hour())

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
@app.post("/todo")
def add_task(task : Annotated[str, Form()]):
    todos.append(task)
    return RedirectResponse("/mirror_dashboard", status_code=303)


@app.get("/get_todo")
def get_todo():
    return StreamingResponse(media_type="text/event-stream", content=get_todo())


async def get_todo():
    while True:
        await asyncio.sleep(1)
        tasks = json.dumps(todos)
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
