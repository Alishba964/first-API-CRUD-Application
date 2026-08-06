class TaskService:
    def __init__(self, repository):
        self.repository = repository

    def list_tasks(self):
        return self.repository.get_all()

    def get_task(self, task_id):
        return self.repository.get_by_id(task_id)

    def create_task(self, title):
        if not title.strip():
            raise ValueError("Title cannot be empty")
        return self.repository.create(title)

    def update_task(self, task_id, title, done):
        if not title.strip():
            raise ValueError("Title cannot be empty")
        return self.repository.update(task_id, title, done)

    def delete_task(self, task_id):
        return self.repository.delete(task_id)