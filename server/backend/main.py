from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Body
import uvicorn
import json
import os

import paths

import db_helper as db
db.setup()

import tasks

app = FastAPI()

with open("version.json") as f:
    version_id = json.load(f)["version_id"]

@app.get("/api/version")
async def get_version():
    return {
        "version_id": version_id
    }

@app.get("/api/tasks")
async def get_tasks():
    return tasks.get_tasks()

@app.post("/api/tasks/next")
async def get_next_task(
    allowed_scripts: list[str] = Body(..., embed=True)
):
    found_task = tasks.get_next_task(allowed_scripts)
    if not found_task:
        return {"found": False}
    
    id = found_task["id"]
    tasks.start_run(id)
    with open(os.path.join(paths.UPCOMING_RUNS, f"{id}.json"), "r") as f:
        data = json.load(f)
    found_task = {**found_task, **data}
    found_task["found"] = True
    
    return found_task

@app.post("/api/tasks/create")
async def create_task(
    script: str = Body(...),
    priority: str = Body(...),
    data: dict = Body(...)
):
    return tasks.create_task(script, data, priority)

@app.post("/api/runs/complete")
async def complete_run(
    data: UploadFile = File(...),
    files: List[UploadFile] = File(...),
):
    data = json.loads(data.file.read())
    return tasks.complete_run(data, files)

@app.get("/api/files/info/{path:path}")
async def get_file(path: str):
    fs_path = safe_get_file_path(path)
    if fs_path == None:
        return
    
    if os.path.isdir(fs_path):
        children = os.listdir(fs_path)
        return {
            "type": "folder",
            "children": children
        }
    else:
        return {
            "type": "file"
        }

@app.get("/api/files/download/{path:path}")
async def read_file(path: str):
    fs_path = safe_get_file_path(path)
    if fs_path == None:
        return
    
    if not os.path.exists(fs_path):
        return
    if os.path.isdir(fs_path):
        return
    
    return FileResponse(fs_path)

def safe_get_file_path(path):
    fs_path = os.path.join(paths.FILES, path)
    if os.path.commonpath([paths.FILES, fs_path]) != paths.FILES:
        return None
    if not os.path.exists(fs_path):
        return None
    return fs_path

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)