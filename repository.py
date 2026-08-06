import sqlite3
import psycopg2
import psycopg2.extras
import os

DB_FILE = "tasks.db"


# ---------- In-memory (kept for reference / tests) ----------
class InMemoryRepository:
    def __init__(self):
        self.tasks = [
            {"id": 1, "title": "Buy milk", "done": False},
            {"id": 2, "title": "Walk the dog", "done": True},
            {"id": 3, "title": "Finish assignment", "done": False},
        ]
        self.next_id = 4

    def get_all(self):
        return self.tasks

    def get_by_id(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def create(self, title):
        task = {"id": self.next_id, "title": title, "done": False}
        self.tasks.append(task)
        self.next_id += 1
        return task

    def update(self, task_id, title, done):
        task = self.get_by_id(task_id)
        if task is None:
            return None
        task["title"] = title
        task["done"] = done
        return task

    def delete(self, task_id):
        task = self.get_by_id(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True


# ---------- Postgres ----------
class PostgresRepository:
    def __init__(self, connection_url):
        self.connection_url = connection_url
        self._init_db()

    def _get_connection(self):
        return psycopg2.connect(self.connection_url, cursor_factory=psycopg2.extras.RealDictCursor)

    def _init_db(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)
        cur.execute("SELECT COUNT(*) FROM tasks")
        count = cur.fetchone()["count"]
        if count == 0:
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                [("Buy milk", False), ("Walk the dog", True), ("Finish assignment", False)]
            )
        conn.commit()
        cur.close()
        conn.close()

    def get_all(self):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = [dict(row) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return rows

    def get_by_id(self, task_id):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return dict(row) if row else None

    def create(self, title):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(row)

    def update(self, task_id, title, done):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return None
        cur.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (title, done, task_id)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return dict(row)

    def delete(self, task_id):
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            return False
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True