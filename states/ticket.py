from aiogram.fsm.state import StatesGroup, State
class CreateTicket(StatesGroup):
    text = State()
    photo = State()