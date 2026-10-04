from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import httpx
from config import LAT, LON

router = APIRouter(
    prefix="/weather",
    tags=["Weather"]
)


@router.get("/get_curr_weather_data")
async def get_curr_weather_data():
    """
    Streaming Response to js script from get_curr_weather function
    """
    return StreamingResponse(media_type="text/event-stream",content=get_curr_weather())


# async func for weather api
async def get_curr_weather():
    """
    Fetch weather data from open-meteo every 5 seconds and yield :
    "<temperature in celsius> | <windspeed>"

    If a fetch fails, the last known value is yielded again
    (nothing is yielded until a first fetch has succeeded).
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    last_data = None

    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            await asyncio.sleep(5)
            try:
                response = await client.get(url)
                response.raise_for_status()
                weather_data = response.json()['current_weather']
                last_data = f"{weather_data['temperature']} | {weather_data['windspeed']}"
            except (httpx.HTTPError, KeyError, ValueError) as e:
                print(f"Weather fetch failed: {e!r}")

            if last_data is not None:
                yield f"data: {last_data}\n\n"
