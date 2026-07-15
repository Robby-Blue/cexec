from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi import Body
import uvicorn
import json

import db_helper as db
db.setup()

import tasks
import webhooks

app = FastAPI()

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/api/tasks")
async def get_tasks():
    return tasks.get_tasks()

@app.post("/api/tasks/next")
async def get_next_task(
    allowed_scripts: list[str] = Body(..., embed=True)
):
    found_tasks = tasks.get_next_task(allowed_scripts)
    if not found_tasks:
        return 404
    
    task = found_tasks[0]
    tasks.start_run(task["id"])
    
    return task

@app.post("/api/tasks/create")
async def create_task(
    script: str = Body(...),
    path: str = Body(...)
):
    return tasks.create_task(script, path)

@app.post("/api/runs/complete")
async def complete_run(
    data: UploadFile = File(...),
    files: List[UploadFile] = File(...),
):
    data = json.loads(data.file.read())
    return tasks.complete_run(data, files)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)