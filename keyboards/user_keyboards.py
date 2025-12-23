from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📄 Мой профиль"))
    builder.row(KeyboardButton(text="ℹ Информация"), KeyboardButton(text="❓ Помощь"))
    builder.row(KeyboardButton(text="📝 Оставить заявку"))
    builder.row(KeyboardButton(text="📚 Мои заявки"))
    return builder.as_markup(resize_keyboard=True)