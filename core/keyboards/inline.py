from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_confirm_bn_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Добавить ссылку', callback_data='add_bn')
    keyboard_builder.button(text='Не добавлять ссылку', callback_data='no_bn')
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()