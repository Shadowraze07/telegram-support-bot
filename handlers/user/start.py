import re
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database.queries import get_user, add_user
from states.register import Register
from keyboards.user_keyboards import main_menu_kb
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

router = Router()

def confirm_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ Все верно"), KeyboardButton(text="❌ Заново"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

@router.message(Command("cancel"))
@router.message(F.text.lower() == "отмена")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=main_menu_kb())

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(f"👋 С возвращением, {user.name}!", reply_markup=main_menu_kb())
    else:
        sent_msg = await message.answer("Добро пожаловать! Введите ваше имя:")
        # Сохраняем ID сообщения, чтобы потом его удалить (Живой интерфейс)
        await state.update_data(last_msg_id=sent_msg.message_id)
        await state.set_state(Register.name)

@router.message(Register.name)
async def reg_name(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) < 2 or len(message.text) > 50:
        return await message.answer("❌ Имя от 2 до 50 символов. Введите снова:")
    
    data = await state.get_data()
    # Удаляем предыдущий вопрос бота и ответ пользователя для чистоты
    try:
        await message.bot.delete_message(message.chat.id, data['last_msg_id'])
        await message.delete()
    except: pass

    await state.update_data(name=message.text)
    sent_msg = await message.answer("Шаг 2: Введите вашу группу:")
    await state.update_data(last_msg_id=sent_msg.message_id)
    await state.set_state(Register.group)

@router.message(Register.group)
async def reg_group(message: types.Message, state: FSMContext):
    if not message.text or len(message.text) > 20:
        return await message.answer("❌ Название группы слишком длинное. Введите снова:")

    data = await state.get_data()
    try:
        await message.bot.delete_message(message.chat.id, data['last_msg_id'])
        await message.delete()
    except: pass

    await state.update_data(group=message.text)
    sent_msg = await message.answer("Шаг 3: Введите телефон или напишите 'нет':")
    await state.update_data(last_msg_id=sent_msg.message_id)
    await state.set_state(Register.phone)

@router.message(Register.phone)
async def reg_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone.lower() != 'нет' and not re.match(r'^\+?[\d\s\-]{10,15}$', phone):
        return await message.answer("❌ Неверный формат. Попробуйте снова или напишите 'нет':")

    data = await state.get_data()
    try:
        await message.bot.delete_message(message.chat.id, data['last_msg_id'])
        await message.delete()
    except: pass

    await state.update_data(phone=phone)
    summary = (f"📋 **Проверьте ваши данные:**\n\n👤 Имя: {data['name']}\n"
               f"👥 Группа: {data['group']}\n📞 Тел: {phone}\n\nВсе верно?")
    
    sent_msg = await message.answer(summary, reply_markup=confirm_kb(), parse_mode="Markdown")
    await state.update_data(last_msg_id=sent_msg.message_id)
    await state.set_state(Register.confirm)

@router.message(Register.confirm, F.text == "✅ Все верно")
async def reg_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone_val = data['phone'] if data['phone'].lower() != 'нет' else None
    await add_user(message.from_user.id, data['name'], data['group'], phone_val)
    
    try:
        await message.bot.delete_message(message.chat.id, data['last_msg_id'])
        await message.delete()
    except: pass
    
    await state.clear()
    await message.answer("🎉 Регистрация завершена!", reply_markup=main_menu_kb())

@router.message(Register.confirm, F.text == "❌ Заново")
async def reg_restart(message: types.Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer("Начнем сначала. Введите имя:")