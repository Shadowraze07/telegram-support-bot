from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Главное меню админа
def admin_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="👥 Список пользователей"))
    builder.row(KeyboardButton(text="📝 Список заявок"))
    builder.row(KeyboardButton(text="🏠 Выйти из админки"))
    return builder.as_markup(resize_keyboard=True)

# Клавиатура для новых УВЕДОМЛЕНИЙ
def ticket_manage_kb(ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙ В обработку", callback_data=f"stat_proc_{ticket_id}")
    builder.button(text="✅ Ответить", callback_data=f"stat_repl_{ticket_id}")
    builder.button(text="❌ Отклонить", callback_data=f"stat_rejc_{ticket_id}")
    builder.adjust(1)
    return builder.as_markup()

# Клавиатура для СПИСКА заявок 
def ticket_status_only_kb(ticket_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙ В обработку", callback_data=f"stat_proc_{ticket_id}")
    builder.button(text="❌ Отклонить", callback_data=f"stat_rejc_{ticket_id}")
    builder.adjust(2)
    return builder.as_markup()

def ticket_filters_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🆕 Новые", callback_data="filter_Новая")
    builder.button(text="⚙ В обработке", callback_data="filter_В обработке")
    builder.button(text="✅ Отвеченные", callback_data="filter_Отвечено")
    builder.button(text="❌ Отклоненные", callback_data="filter_Отклонено")
    builder.adjust(2)
    return builder.as_markup()