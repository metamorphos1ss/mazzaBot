from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message

from core.utils.dbconnect import Request

async def userdb_init(message: Message, request: Request):
    await request.add_data(message.from_user.id, message.from_user.username)

async def get_start(message: Message, request: Request, storage):
    await request.add_data(message.from_user.id, message.from_user.username)
    storage_key = StorageKey(chat_id=-1, user_id=-1, bot_id=message.bot.id)

    data = await storage.get_data(key=storage_key)
    start_text = data.get("start_text", "default text2")

    await message.answer(start_text, parse_mode=ParseMode.MARKDOWN_V2)