from aiogram import Router, types, F
from database.queries import get_user

router = Router()

@router.message(F.text == "📄 Мой профиль")
async def profile_handler(message: types.Message):
    user = await get_user(message.from_user.id)
    
    if user:
        text = (
            f"👤 **Ваш профиль**\n\n"
            f"🆔 **ID:** `{user.telegram_id}`\n"
            f"👤 **Имя:** {user.name}\n"
            f"👥 **Группа:** {user.group}\n"
            f"📞 **Телефон:** {user.phone if user.phone else 'не указан'}\n"
            f"📅 **Дата регистрации:** {user.created_at.strftime('%d.%m.%Y')}"
        )
        await message.answer(text, parse_mode="Markdown")
    else:
        await message.answer("Ошибка: профиль не найден. Попробуйте /start")