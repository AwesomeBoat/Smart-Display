from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from datetime import datetime
import asyncio


app = FastAPI()

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

# Async func for /hour route
async def hour():
    while True:
        await asyncio.sleep(1)
        now = datetime.now()
        yield f"data: {now}\n\n"
