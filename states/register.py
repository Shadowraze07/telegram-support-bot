from aiogram.fsm.state import StatesGroup, State
class Register(StatesGroup):
    name = State()
    group = State()
    phone = State()
    confirm = State()