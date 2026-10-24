import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config  # <-- Используем асинхронный инструмент сборки

from alembic import context
from database import Base  # <-- Подключаем Архитектора
from models import Task              # <-- Подключаем модели

# Загружаем скрытый файл .env
load_dotenv()

# Это объект конфигурации Alembic
config = context.config

# Перезаписываем адрес БД в конфигурации значением из секретного .env
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Связываем Alembic с журналом нашего Архитектора
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в автономном (offline) режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Вспомогательная функция для физического применения шагов миграции."""
    context.configure(
        connection=connection, 
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаем асинхронное подключение и безопасно запускаем миграции."""
    # Используем правильную асинхронную фабрику движка
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync позволяет запустить синхронный контекст Alembic внутри асинхронного тоннеля
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в режиме реального подключения (online)."""
    import asyncio
    # Запускаем асинхронную функцию через стандартный цикл событий Python
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
