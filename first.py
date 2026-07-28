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


