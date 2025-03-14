from aiogram.fsm.state import State, StatesGroup

class Steps(StatesGroup):
    get_message = State()
    button = State()
    get_text_button = State()
    get_url_button = State()