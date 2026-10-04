from fastapi import APIRouter, Form, HTTPException
import asyncio
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import Annotated
import json
from data.db import get_db


router = APIRouter(
    prefix="/todo",
    tags=["Todo"]
)


@router.get("/get_curr_todo")
async def get_curr_todo():
    """
    Streaming Response to js script from get_todo function
    """
    return StreamingResponse(media_type="text/event-stream", content=get_todo())


async def get_todo():
    """
    Returns all tasks of active profile from task table in display.db 
    """
    while True:
        await asyncio.sleep(1)
        with get_db() as con:
            cur = con.cursor()
            tasks = json.dumps([dict(row) for row in cur.execute(command).fetchall()])
            yield f"data: {tasks}\n\n"



@router.get("/get_tasks")
async def get_tasks():
    """
    Return all tasks from task table as a list of dicts
    """
    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM task")
        return [dict(row) for row in cur.fetchall()]


@router.post("/add_task", status_code=201)
async def add_task(task : Annotated[str, Form()]):
    """
    Add a task to the task table and return it
    """
    with get_db() as con:
        cur = con.cursor()
        now = datetime.now().strftime("%H:%M:%S")
        command = "INSERT INTO task (name, created_at) VALUES (?, ?)"
        cur.execute(command, (task,now))
        return {"id": cur.lastrowid, "name": task, "created_at": now, "done": 0}


@router.patch("/toggle_task/{id}")
async def toggle_task(id: int):
    """
    Check or uncheck a task (done 0 <-> 1) and return it
    """
    with get_db() as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM task WHERE id = ?", (id,))
        task = cur.fetchone()
        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        new_done = 0 if task["done"] else 1
        cur.execute("UPDATE task SET done = ? WHERE id = ?", (new_done, id))
        return {**dict(task), "done": new_done}


@router.delete("/delete_task/{id}")
async def delete_task(id: int):
    """
    delete task by it's id
    """
    with get_db() as con:
        cur = con.execute(
            "DELETE FROM task WHERE id = ?",
            (id,)
        )
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
    return {
        "success": True,
        "message": f"Task {id} deleted"
    }

