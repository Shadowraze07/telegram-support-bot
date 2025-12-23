from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database.queries import update_ticket_status

from config import config
from database.queries import (
    get_all_users, 
    get_all_tickets, 
    get_user_by_ticket_id, 
    update_ticket_status,
    get_tickets_by_status
)
from keyboards.admin_keyboards import (
    admin_main_kb, 
    ticket_manage_kb, 
    ticket_status_only_kb,
    ticket_filters_kb
)
from keyboards.user_keyboards import main_menu_kb

router = Router()

# Группа состояний для админской части (ТЗ п. 2.5)
class AdminReply(StatesGroup):
    waiting_for_reply_text = State()

# --- ВХОД В АДМИНКУ ---

@router.message(Command("admin"))
async def admin_start(message: types.Message):
    """Проверка прав доступа и запуск админ-панели (ТЗ п. 2.5)"""
    if message.from_user.id in config.ADMIN_IDS:
        # Живой интерфейс: удаляем команду /admin для чистоты чата
        await message.delete() 
        await message.answer("⚙️ **Админ-панель активирована**", reply_markup=admin_main_kb())
    else:
        await message.answer("❌ Доступ запрещен.")

# --- РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ---

@router.message(F.text == "👥 Список пользователей")
async def view_users(message: types.Message):
    """Вывод списка всех зарегистрированных пользователей (ТЗ п. 2.5)"""
    if message.from_user.id not in config.ADMIN_IDS: return
    
    users = await get_all_users()
    if not users:
        return await message.answer("В базе еще нет зарегистрированных пользователей.")
        
    res = "👥 **Зарегистрированные студенты:**\n\n"
    for u in users:
        res += f"• {u.name} | Группа: {u.group} | ID: `{u.telegram_id}`\n"
    
    await message.answer(res, parse_mode="Markdown")

# --- РАБОТА С ЗАЯВКАМИ (ФИЛЬТРЫ И ЖИВОЙ ИНТЕРФЕЙС) ---

@router.message(F.text == "📝 Список заявок")
async def ask_ticket_filter(message: types.Message):
    """Вызов меню фильтрации заявок по статусам (ТЗ п. 2.5)"""
    if message.from_user.id not in config.ADMIN_IDS: return
    await message.answer("🔍 Выберите статус заявок для просмотра:", 
                         reply_markup=ticket_filters_kb())

@router.callback_query(F.data.startswith("filter_"))
async def show_filtered_tickets(callback: types.CallbackQuery):
    """Отображение заявок по выбранному фильтру (ТЗ п. 2.5)"""
    status = callback.data.split("_")[1]
    tickets_data = await get_tickets_by_status(status)
    
    # Живой интерфейс: редактируем сообщение выбора вместо отправки нового
    if not tickets_data:
        await callback.answer(f"Нет заявок со статусом {status}")
        return await callback.message.edit_text(
            f"📭 Заявок со статусом **'{status}'** не найдено.", 
            reply_markup=ticket_filters_kb(),
            parse_mode="Markdown"
        )
    
    await callback.answer()
    # Удаляем сообщение с кнопками фильтров перед выводом списка
    await callback.message.delete()
    
    for ticket, user_name in tickets_data:
        msg_text = (f"🆔 **№{ticket.id}** | От: {user_name}\n"
                    f"💬 Текст: {ticket.text}\n"
                    f"📊 Статус: **{ticket.status}**")
        
        await callback.message.answer(
            msg_text, 
            reply_markup=ticket_status_only_kb(ticket.id),
            parse_mode="Markdown"
        )

# --- ОБРАБОТКА СТАТУСОВ ---

@router.callback_query(F.data.startswith("stat_proc_"))
async def process_status_in_work(callback: types.CallbackQuery):
    """Перевод заявки в статус 'В обработке' (ТЗ п. 2.4)"""
    ticket_id = int(callback.data.split("_")[2])
    await update_ticket_status(ticket_id, "В обработке")
    
    # Живой интерфейс: обновляем текст сообщения на месте
    update_text = "\n\n⚙️ **Статус изменен: В обработке**"
    if callback.message.caption:
        await callback.message.edit_caption(caption=callback.message.caption + update_text, parse_mode="Markdown")
    else:
        # Заменяем старый статус в тексте для наглядности
        new_text = callback.message.text.replace("Новая", "В обработке")
        await callback.message.edit_text(text=new_text + update_text, 
                                         reply_markup=callback.message.reply_markup, 
                                         parse_mode="Markdown")
    await callback.answer("Статус обновлен")

@router.callback_query(F.data.startswith("stat_rejc_"))
async def process_status_rejected(callback: types.CallbackQuery):
    """Отклонение заявки и удаление кнопок управления (ТЗ п. 2.4)"""
    ticket_id = int(callback.data.split("_")[2])
    await update_ticket_status(ticket_id, "Отклонено")
    
    # Живой интерфейс: удаляем кнопки, чтобы нельзя было изменить статус повторно
    if callback.message.caption:
        await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ **Статус: Отклонено**", reply_markup=None)
    else:
        await callback.message.edit_text(text=callback.message.text + "\n\n❌ **Статус: Отклонено**", reply_markup=None)
    await callback.answer("Заявка отклонена")

# --- ЛОГИКА ОТВЕТА ПОЛЬЗОВАТЕЛЮ ---

@router.callback_query(F.data.startswith("stat_repl_"))
async def process_reply_start(callback: types.CallbackQuery, state: FSMContext):
    """Инициализация процесса ответа на заявку (ТЗ п. 2.5)"""
    ticket_id = int(callback.data.split("_")[2])
    # Сохраняем ID сообщения, чтобы позже убрать из него кнопки
    await state.update_data(reply_ticket_id=ticket_id, original_msg_id=callback.message.message_id)
    
    await callback.answer()
    await callback.message.answer(f"✍️ Введите ваш ответ для заявки №{ticket_id}:")
    await state.set_state(AdminReply.waiting_for_reply_text)

@router.message(AdminReply.waiting_for_reply_text)
async def send_reply_to_user(message: types.Message, state: FSMContext, bot: Bot):
    """Отправка сообщения пользователю и финализация заявки (ТЗ п. 2.5)"""
    data = await state.get_data()
    ticket_id = data['reply_ticket_id']
    orig_msg_id = data['original_msg_id']
    
    user_tg_id = await get_user_by_ticket_id(ticket_id)
    
    if user_tg_id:
        try:
            # Отправка ответа в личные сообщения пользователю
            await bot.send_message(
                user_tg_id, 
                f"✉️ **Ответ по вашей заявке №{ticket_id}:**\n\n{message.text}",
                parse_mode="Markdown"
            )
            # Автоматическая смена статуса после ответа
            await update_ticket_status(ticket_id, "Отвечено")
            
            # Живой интерфейс: убираем кнопки из сообщения с заявкой
            try:
                await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=orig_msg_id, reply_markup=None)
            except: pass
                
            await message.answer(f"✅ Ответ отправлен, статус №{ticket_id} изменен на 'Отвечено'.")
        except Exception as e:
            await message.answer(f"❌ Ошибка отправки: {e}")
    else:
        await message.answer("❌ Пользователь не найден.")
    
    # Живой интерфейс: удаляем текст ответа админа из чата для чистоты
    await message.delete()
    await state.clear()

# --- ВЫХОД ---

@router.message(F.text == "🏠 Выйти из админки")
async def exit_admin(message: types.Message):
    """Возврат в пользовательское меню"""
    await message.answer("Выход в меню пользователя...", reply_markup=main_menu_kb())