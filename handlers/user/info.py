from aiogram import Router, types, F

router = Router()

@router.message(F.text == "ℹ Информация")
async def info_handler(message: types.Message):
    await message.answer(
        "🏫 **Наш колледж**\n\n"
        "Я создал этого бота чтобы закрыть модуль.\n"
        "Здесь вы можете оставить запрос администратору и отслеживать его статус.",
        parse_mode="Markdown"
    )
