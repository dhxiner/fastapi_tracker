import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 1. Загружаем переменные из файла .env в систему
load_dotenv()

# Достаем строку подключения из .env
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Создаем асинхронный "движок" (Engine)
# Он отвечает за физическое удержание соединений с PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True) 
# echo=True заставит SQLAlchemy выводить в консоль все SQL-запросы, которые она делает под капотом. 
# Это мега-удобно для обучения!

# 3. Создаем фабрику сессий (Sessionmaker)
# Каждый раз, когда юзер будет делать запрос к API, мы будем выдавать ему свежую сессию
async_session = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 4. Создаем базовый класс для будущих таблиц (моделей)
# Все наши таблицы на Python будут наследоваться от этого класса Base
class Base(DeclarativeBase):
    pass


# 5. Функция-помощник (Dependency Injection) для FastAPI
# Она будет открывать сессию перед запросом и автоматически закрывать её после ответа сервера
async def get_db():
    async with async_session() as session:
        yield session