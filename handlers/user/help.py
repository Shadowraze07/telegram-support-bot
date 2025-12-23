from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def help_handler(message: types.Message):
    text = (
        "❓ **Как пользоваться ботом?**\n\n"
        "1. **Заявки:** Нажмите «Оставить заявку», введите текст и (по желанию) прикрепите фото.\n"
        "2. **Профиль:** Используйте кнопки меню. /cancel для отмены..\n"
        "3. **Статус:** В разделе «Мои заявки» можно увидеть, на какой стадии ваше обращение.\n\n"
        "Если возникли технические проблемы, обратитесь к старосте группы или администратору."
    )
    await message.answer(text, parse_mode="Markdown")