from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from database.queries import add_ticket, get_my_tickets
from states.ticket import CreateTicket
from config import config
from keyboards.user_keyboards import main_menu_kb
from keyboards.admin_keyboards import ticket_manage_kb

router = Router()

@router.message(F.text == "📝 Оставить заявку")
async def start_ticket(message: types.Message, state: FSMContext):
    await state.set_state(CreateTicket.text)
    await message.answer("💬 Опишите вашу проблему:")

@router.message(CreateTicket.text)
async def ticket_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await state.set_state(CreateTicket.photo)
    await message.answer("📸 Пришлите ОДНО фото или напишите 'нет', если оно не требуется.")

@router.message(CreateTicket.photo)
async def ticket_photo(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    # Обработка фото
    photo_id = message.photo[-1].file_id if message.photo else None
    
    # Сохранение в БД
    tid = await add_ticket(message.from_user.id, data['text'], photo_id)
    await state.clear()
    
    if tid:
        await message.answer(f"✅ Заявка №{tid} создана! Ожидайте ответа.", reply_markup=main_menu_kb())
        
        # Уведомление всем админам с кнопками управления
        for admin_id in config.ADMIN_IDS:
            try:
                msg_text = f"🔔 **Новая заявка №{tid}**\n\n💬 Текст: {data['text']}"
                if photo_id:
                    await bot.send_photo(admin_id, photo=photo_id, caption=msg_text, reply_markup=ticket_manage_kb(tid))
                else:
                    await bot.send_message(admin_id, msg_text, reply_markup=ticket_manage_kb(tid))
            except Exception:
                pass
    else:
        await message.answer("❌ Ошибка при создании заявки. Попробуйте снова через /start")

@router.message(F.text == "📚 Мои заявки")
async def my_tickets_handler(message: types.Message):
    tickets = await get_my_tickets(message.from_user.id)
    if not tickets:
        return await message.answer("У вас пока нет созданных заявок.")
    
    res = "📊 **История ваших обращений:**\n\n"
    for t in tickets:
        res += f"🔸 №{t.id} | Статус: **{t.status}**\n"
    await message.answer(res, parse_mode="Markdown")