from aiogram.fsm.state import State, StatesGroup

class Commands(StatesGroup):
    get_command = State()
    get_text = State()