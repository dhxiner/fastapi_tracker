from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

TASKS_DB = []

class TaskCreate(BaseModel):
    title: str # название задачи (строка)
    description: str #описание задачи(строка)
#1. Получить все задачи (Метод GET)
@app.get("/tasks")
def get_tasks():
    return {"tasks": TASKS_DB}

#2. Добавить новую задачу (Метод POST)
@app.post("/tasks")
def create_task(task: TaskCreate):
    # Превращаем данные от пользователя в обычный словарь Python
    new_task = {
        "id": len(TASKS_DB) + 1, # Генерируем простой ID(1, 2, 3...)
        "title": task.title,
        "description": task.description,
        "completed": False # По умолчанию не выполнено
    }
    # Добавляем в нашу "базу данных"
    TASKS_DB.append(new_task)
    return {"message": "Задача успешно добавлена!", "task": new_task}