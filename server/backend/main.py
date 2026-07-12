from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Body
import uvicorn

import db_helper as db
db.setup()

import tasks

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
    tasks.mark_started(task["id"])
    
    return task

@app.post("/api/tasks/create")
async def create_task(
    script: str = Body(...),
    path: str = Body(...)
):
    return tasks.create_task(script, path)

@app.post("/api/tasks/mark_completed")
async def mark_completed(
    id: str = Body(..., embed=True),
):
    return tasks.mark_completed(id)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)