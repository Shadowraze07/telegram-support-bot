import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from config import config

# Импорт роутеров
from handlers.user import start, tickets, info, help
from handlers.admin import admin_menu
from database.db import init_db

# --- НАСТРОЙКА ЛОГИРОВАНИЯ ---

# Создаем папку logs, если её нет
if not os.path.exists('logs'):
    os.makedirs('logs')

# Настройка логирования: уровни INFO, WARNING, ERROR 
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log", encoding='utf-8'), # Запись в файл 
        logging.StreamHandler() # Вывод в консоль для удобства разработки
    ]
)

logger = logging.getLogger(__name__)

async def main():
    # Инициализация базы данных
    await init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(info.router)
    dp.include_router(help.router)
    dp.include_router(tickets.router)
    dp.include_router(admin_menu.router)

    # Логирование запуска бота 
    logger.info("Бот успешно запущен и готов к работе")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        # Логирование критических ошибок 
        logger.error(f"Критическая ошибка при работе бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот остановлен")