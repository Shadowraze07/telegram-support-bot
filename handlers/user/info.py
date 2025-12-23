from aiogram import Router, types, F
from aiogram.filters import StateFilter

router = Router()

# Используем .contains(), чтобы игнорировать любые символы вокруг слова
@router.message(F.text.contains("Информация"), StateFilter("*"))
async def info_handler(message: types.Message):
    await message.answer(
        "🏫 **Наш колледж**\n\n"
        "Я создал этого бота, чтобы закрыть модуль.\n"
        "Здесь вы можете оставить запрос администратору и отслеживать его статус.",
        parse_mode="Markdown"
    )