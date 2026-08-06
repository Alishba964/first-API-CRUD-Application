import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from repository import PostgresRepository
from service import TaskService

load_dotenv()

app = FastAPI()

repository = PostgresRepository(os.getenv("DATABASE_URL"))
service = TaskService(repository)


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool = False


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return service.list_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    try:
        return service.create_task(new_task.title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated: TaskUpdate):
    try:
        task = service.update_task(task_id, updated.title, updated.done)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return