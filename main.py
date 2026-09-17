from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from datetime import datetime
import asyncio
import httpx
from dotenv import load_dotenv
import os




app = FastAPI()
load_dotenv()

LAT = os.getenv("LAT")
LON = os.getenv("LON")



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


    
# Async func for /hour route
async def hour():
    while True:
        await asyncio.sleep(1)
        now = datetime.now().strftime("%H:%M:%S")
        yield f"data: {now}\n\n"


# async func for weather api
async def get_curr_weather():
    while True:
        await asyncio.sleep(60)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true" 
        response = httpx.get(url).json()
        weather_data = response['current_weather']
        data = {"temperature:":weather_data['temperature'],
                "windspeed":weather_data['windspeed']}
        yield f"data: {data['temperature:']}°C | Wind {data['windspeed']}\n\n"
