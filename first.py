from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()
DB_file="task.db"

def get_connection():
    conn=sqlite3.connect(DB_file)
    conn.row_factory=sqlite3.Row
    return conn

def init_db():
    conn=get_connection()
    cur=conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
    )""")

    cur.execute("""SELECT COUNT(*) FROM tasks""")
    count = cur.fetchone()[0]

    if count==0:
        cur.executemany(
            "INSERT INTO tasks(title,done) VALUES(?,?)",
            [("Buy Milk",0),("Finish Assignment",1),("sleep",0)]
        )
        conn.commit()
        conn.close()

init_db()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    done: bool = False


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return dict(row)


@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    if not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (new_task.title, False)
    )
    conn.commit()
    new_id = cur.lastrowid

    cur.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    row = cur.fetchone()
    conn.close()

    return dict(row)