from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.utils import keyboard

from core.keyboards.inline import get_confirm_bn_keyboard

from core.utils.ad_list import AdList
from core.utils.ad_state import Steps
from core.utils.dbconnect import Request


async def get_ad(message: Message, command: CommandObject, state: FSMContext):
    await message.answer(f'Начинаю создавать пост.\r\n\r\n'
                         f'Отправь рекламный пост (в дальнейшем можно будет добавить под него кнопку-ссылку)')

    await state.set_state(Steps.get_message)

async def get_message(message: Message, state: FSMContext):
    await message.answer(f'Пост сохранен. \r\n'
                         f'Будем добавлять ссылку?', reply_markup=get_confirm_bn_keyboard())
    await state.update_data(message_id=message.message_id, chat_id=message.from_user.id)
    await state.set_state(Steps.button)

async def button(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    if callback_query.data == 'add_bn':
        await callback_query.message.answer(f'Отправь текст для кнопки-ссылки', reply_markup=None)
        await state.set_state(Steps.get_text_button)
    elif callback_query.data == 'no_bn':
        await callback_query.message.edit_reply_markup(reply_markup=None)
        data = await state.get_data()
        message_id = data.get('message_id')
        chat_id = data.get('chat_id')
        await confirm(callback_query.message, bot, message_id, chat_id)
        await state.set_state(Steps.get_url_button)

    await callback_query.answer()

async def get_text_button(message: Message, state: FSMContext):
    await state.update_data(text_button=message.text)
    await message.answer(f'Теперь отправь ссылку для кнопки')
    await state.set_state(Steps.get_url_button)

async def get_url_button(message: Message, bot: Bot, state: FSMContext):
    await state.update_data(url_button=message.text)
    added_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=(await state.get_data()).get('text_button'),
                # может быть ошибка снизу 10:54
                url=(await state.get_data()).get('url_button')
            )
        ]
    ])
    data = await state.get_data()
    message_id = data.get('message_id')
    chat_id = data.get('chat_id')
    await confirm(message, bot, message_id, chat_id, added_kb)

async def confirm(message: Message, bot: Bot, message_id: int, chat_id: int, reply_markup: InlineKeyboardMarkup = None):
    await bot.copy_message(chat_id, chat_id, message_id, reply_markup=reply_markup)
    await message.answer(f'Вот пост, который будет отправлен. Подтверди', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Подтвердить', callback_data='confirm_ad'),
        ],
        [
            InlineKeyboardButton(text='Отменить', callback_data='cancel_ad'),
        ]
    ]))


async def ad_decide(callback_query: CallbackQuery, bot: Bot, state: FSMContext, request: Request, adlist: AdList):
    data = await state.get_data()
    message_id = data.get('message_id')
    chat_id = data.get('chat_id')
    text_button = data.get('text_button')
    url_button = data.get('url_button')

    if callback_query.data == 'confirm_ad':
        callback_query.message.edit_text(f'Начинаю рассылку', reply_markup=None)

        if not await request.check_table():
            await request.create_table()

        count = await adlist.broadcast(chat_id, message_id, text_button, url_button)
        await callback_query.message.answer(f'Успешно разослали сообщение')
        await request.delete_table()

    elif callback_query.data == 'cancel_ad':
        callback_query.message.answer(f'Отменил рассылку', reply_markup=None)

    await state.clear()
    await callback_query.answer()