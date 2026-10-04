from fastapi import FastAPI
from fastapi.responses import FileResponse


from config import INDEX_PATH, JS_SCRIPT_PATH
# Import widgets
from widgets import calendar, clock, todo, weather, habits




# APP
app = FastAPI()
## Routers
app.include_router(calendar.router)
app.include_router(clock.router)
app.include_router(todo.router)
app.include_router(weather.router)
app.include_router(habits.router)


# API 
@app.get("/")
async def health():
    return {"status": "ok"}


# Path to html index file
@app.get("/display_dashboard")
async def get_display_dashboard():
    return FileResponse(INDEX_PATH)

# Path to js file
@app.get("/script.js")
async def get_js_file():
    return FileResponse(JS_SCRIPT_PATH)



