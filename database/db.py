import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base  # Импорт базового класса моделей для создания таблиц

# 1. Настройка асинхронного движка
# Используем SQLite с драйвером aiosqlite для полной асинхронности
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=False)

# 2. Настройка фабрики сессий
# async_session будет использоваться во всех функциях в queries.py
async_session = async_sessionmaker(engine, expire_on_commit=False)

# 3. Функция инициализации базы данных
async def init_db():
    """
    Создает все таблицы (users, tickets) в файле базы данных, 
    если они еще не созданы.
    """
    try:
        async with engine.begin() as conn:
            # Выполняем создание таблиц на основе метаданных моделей
            await conn.run_sync(Base.metadata.create_all)
        logging.info("База данных успешно инициализирована.") # Логирование
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}") # Логирование ошибокimport logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models import Base  # Импорт базового класса моделей для создания таблиц

# 1. Настройка асинхронного движка
# Используем SQLite с драйвером aiosqlite для полной асинхронности
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=False)

# 2. Настройка фабрики сессий
# async_session будет использоваться во всех функциях в queries.py
async_session = async_sessionmaker(engine, expire_on_commit=False)

# 3. Функция инициализации базы данных
async def init_db():
    """
    Создает все таблицы (users, tickets) в файле базы данных, 
    если они еще не созданы.
    """
    try:
        async with engine.begin() as conn:
            # Выполняем создание таблиц на основе метаданных моделей
            await conn.run_sync(Base.metadata.create_all)
        logging.info("База данных успешно инициализирована.") # Логирование по ТЗ п. 6.0
    except Exception as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}") # Логирование ошибок