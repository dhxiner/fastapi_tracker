from sqlalchemy.orm import Mapped, mapped_column
from database import Base

# Создаем модель задачи. Она унаследует магию от нашего Главного Архитектора (Base)
class Task(Base):
    # __tablename__ говорит системе, как именно будет называться таблица внутри PostgreSQL
    __tablename__ = "tasks"

    # Описываем ячейки (колонки) нашей таблицы:
    
    # 1. Порядковый номер (ID). Превратится в PRIMARY KEY (главный ключ таблицы).
    # Номера будут ставиться автоматически: 1, 2, 3...
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 2. Название задачи (строка текста)
    title: Mapped[str]

    # 3. Подробное описание задачи (строка текста). 
    # Сделаем это поле необязательным (nullable=True), вдруг пользователь оставит его пустым.
    description: Mapped[str | None] = mapped_column(nullable=True)

    # 4. Статус задачи: выполнена или нет. По умолчанию (default) будет False (не выполнена).
    completed: Mapped[bool] = mapped_column(default=False)