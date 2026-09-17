from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Annotated


BASE_DIR = Path(__file__).resolve().parent
FRONT_DIR = BASE_DIR.parent / "front"





class Message(BaseModel):
    message: str


app = FastAPI()


@app.get("/")
def get_base():
    return {"status": "ok"}


@app.get("/dash")
def dash():
    return FileResponse(FRONT_DIR / "index.html")



@app.post("/submit")
def display_post(name: Annotated[str, Form()]):
    return {"name": name}