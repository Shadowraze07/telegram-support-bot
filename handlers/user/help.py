from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter #

router = Router()

@router.message(Command("help"), StateFilter("*"))
@router.message(F.text == "❓ Помощь", StateFilter("*"))
async def help_handler(message: types.Message):
    text = (
        "❓ **Как пользоваться ботом?**\n\n"
        "1. **Заявки:** Нажмите «Отправить заявку», введите текст и прикрепите фото.\n"
        "2. **Профиль:** Используйте кнопки меню. /cancel для отмены.\n"
        "3. **Статус:** В разделе «Мои заявки» можно увидеть стадию обращения.\n\n"
        "При проблемах обратитесь к старосте или администратору."
    )
    await message.answer(text, parse_mode="Markdown")