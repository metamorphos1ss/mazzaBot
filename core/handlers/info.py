from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils import keyboard

from core.keyboards.inline import get_confirm_bn_keyboard

from core.utils.ad_list import AdList
from core.utils.commands_state import Commands

from core.utils.dbconnect import Request


async def get_command(message: Message, state: FSMContext):
    await message.answer(f'Начинаю создавать кастомную команду.\r\n\r\n'
                         f'Отправь команду с "/"\r\nНапример "/help"')

    await state.set_state(Commands.get_command)

async def get_command_message(message: Message, state: FSMContext):
    await state.update_data(command=message.text)
    await message.answer("Введите текст, который будет отправлен при вызове этой команды")
    await state.set_state(Commands.get_text)

async def get_text(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Команда сохранена")
    await confirm(message, bot, state)


async def confirm(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    command = data.get('command')
    text = data.get('text')

    await message.answer(text, parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer(f'Вот пост, который будет отправлен командой {command}. Подтверди', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Подтвердить', callback_data='confirm_cmd'),
        ],
        [
            InlineKeyboardButton(text='Отменить', callback_data='cancel_cmd'),
        ]
    ]))

async def cmd_decide(callback_query: CallbackQuery, state: FSMContext, request: Request):
    data = await state.get_data()
    command = data.get('command')
    text = data.get('text')

    if callback_query.data == 'confirm_cmd':
        callback_query.message.edit_text(f'Готово', reply_markup=None)

        await request.bot_messages_update(command, text)


    elif callback_query.data == 'cancel_cmd':
        await callback_query.message.edit_text(f'Отменил', reply_markup=None)

    await state.clear()
    await callback_query.answer()