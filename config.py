import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    # Превращаем строку из .env в список чисел
    admins_raw = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(i.strip()) for i in admins_raw.split(",") if i.strip()]

config = Config()