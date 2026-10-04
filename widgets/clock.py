from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
from datetime import datetime

router = APIRouter(
    prefix="/clock",
    tags=["Clock"])

@router.get("/get_time")
async def get_time():
    """
    Streaming Response to js script from hour function
    """
    return StreamingResponse(media_type="text/event-stream",content=hour())


async def hour():
    """
    Every second, yield the current time as HH:MM:SS
    """
    while True:
        await asyncio.sleep(1)
        now = datetime.now().strftime("%H:%M:%S")
        yield f"data: {now}\n\n"
