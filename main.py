from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

# Импортируем настройки нашей базы данных и модель таблицы
from database import get_db
from models import Task

app = FastAPI()

# Схема Pydantic для проверки входящих данных (ТЗ для создания задачи)
class TaskCreate(BaseModel):
    title: str
    description: str | None = None  # Описание может быть пустым (None)


# 1. ПОЛУЧИТЬ ВСЕ ЗАДАЧИ ИЗ БАЗЫ ДАННЫХ (Метод GET)
@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    # Формируем SQL-запрос: "Выбрать всё из таблицы tasks"
    query = select(Task)
    
    # Выполняем этот запрос асинхронно внутри нашей сессии базы данных
    result = await db.execute(query)
    
    # scalars().all() превращает сырые строки базы данных в красивый список объектов Python
    tasks = result.scalars().all()
    
    return {"tasks": tasks}


# 2. ДОБАВИТЬ НОВУЮ ЗАДАЧУ В БАЗУ ДАННЫХ (Метод POST)
@app.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    # Создаем новый объект нашей модели таблицы
    new_task = Task(
        title=task.title,
        description=task.description
        # Поля id и completed заполнятся базой данных автоматически (по нашим настройкам)
    )
    
    # Говорим сессии: "Подготовь эту задачу к добавлению"
    db.add(new_task)
    
    # Физически сохраняем задачу в PostgreSQL и закрываем транзакцию
    await db.commit()
    
    # Обновляем наш объект new_task, чтобы база данных вернула нам его сгенерированный ID
    await db.refresh(new_task)
    
    return {"message": "Задача успешно сохранена в PostgreSQL!", "task": new_task}