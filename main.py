from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


from config import FRONT_DIR, INDEX_PATH, PHONE_PATH
from data.db import init_db
# Import widgets
from widgets import calendar, clock, todo, weather, habits
from profiles import profile
from display import stream as display_stream



# Create the tables at startup
init_db()

# APP
app = FastAPI()
## Routers
app.include_router(calendar.router)
app.include_router(clock.router)
app.include_router(todo.router)
app.include_router(weather.router)
app.include_router(habits.router)
app.include_router(profile.router)
app.include_router(display_stream.router)
## Front files (css, js): /static/css/tokens.css -> front/css/tokens.css
app.mount("/static", StaticFiles(directory=FRONT_DIR), name="static")

# API 
@app.get("/")
async def health():
    return {"status": "ok"}


# Path to html index file
@app.get("/display_dashboard")
async def get_display_dashboard():
    return FileResponse(INDEX_PATH)

# Path to the phone remote control page
@app.get("/phone")
async def get_phone():
    return FileResponse(PHONE_PATH)




