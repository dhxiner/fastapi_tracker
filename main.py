from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
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

# 3. ИЗМЕНИТЬ СТАТУС ЗАДАЧИ (Метод PATCH)
# В URL мы передаем id конкретной задачи, которую хотим изменить, например: /tasks/1/complete
@app.patch("/tasks/{task_id}/complete")
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Ищем задачу в базе данных по её ID
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none() # Возвращает задачу или None, если её нет
    
    # 2. Если задача не найдена, возвращаем ошибку 404
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача с таким ID не найдена"
        )
    
    # 3. Меняем статус на противоположный (или просто в True)
    task.completed = True
    
    # 4. Сохраняем изменения в PostgreSQL
    await db.commit()
    await db.refresh(task)
    
    return {"message": "Статус задачи успешно обновлен!", "task": task}

# 4. ОЧИСТИТЬ ВСЕ ВЫПОЛНЕННЫЕ ЗАДАЧИ (Метод DELETE)
# СТАТИЧЕСКИЙ адрес пишем ВЫШЕ, чтобы FastAPI не перепутал его с ID задачи
@app.delete("/tasks/clear-completed")
async def clear_completed_tasks(db: AsyncSession = Depends(get_db)):
    # Формируем запрос: "Удалить из таблицы Task все записи, где completed == True"
    query = delete(Task).where(Task.completed == True)
    
    # Выполняем удаление напрямую в базе данных
    result = await db.execute(query)
    await db.commit()
    
    # Считаем, сколько строк удалила база данных
    deleted_count = result.rowcount
    
    return {
        "message": "Очистка выполненных задач завершена успешно", 
        "deleted_tasks_count": deleted_count
    }


# 5. УДАЛИТЬ ОДНУ КОНКРЕТНУЮ ЗАДАЧУ ПО ID (Метод DELETE)
# ДИНАМИЧЕСКИЙ адрес со значением {task_id} пишем в самый низ
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    # Ищем задачу в БД
    query = select(Task).where(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача для удаления не найдена"
        )
    
    # Удаляем конкретную найденную задачу
    await db.delete(task)
    await db.commit()
    
    return {"message": f"Задача с ID {task_id} успешно удалена из базы данных"}