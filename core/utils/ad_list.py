import logging
from typing import List

import asyncio
from aiogram import Bot
import asyncpg
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asyncpg import Record

from core.utils.config import config


class AdList:
    def __init__(self, bot: Bot, connector: asyncpg.pool.Pool):
        self.bot = bot
        self.connector = connector


    async def get_keyboard(self, text_button, url_button):
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text=text_button, url=url_button)
        keyboard_builder.adjust(1)
        return keyboard_builder.as_markup()


    async def get_users(self):
        async with self.connector.acquire() as connect:
            query = f"SELECT user_id FROM users_ad WHERE status = 'waiting'"
            results_query: List[Record] = await connect.fetch(query)
            return [result.get('user_id') for result in results_query]

    async def update_status(self, user_id, status):
        async with self.connector.acquire() as connect:
            query = f"UPDATE users_ad SET status = '{status}' WHERE user_id = '{user_id}'"
            await connect.execute(query)

    async def send_message(self, user_id: int, from_chat_id: int, message_id: int, keyboard:InlineKeyboardMarkup = None):
        try:
            await self.bot.copy_message(user_id, from_chat_id, message_id, reply_markup=keyboard)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            return await self.send_message(user_id, from_chat_id, message_id, keyboard)
        except Exception as e:
            await self.update_status(user_id, 'error')
        else:
            await self.update_status(user_id, 'success')
            return True

        return False

    async def broadcast(self, from_chat_id: int, message_id: int, text_button: str = None, url_button: str = None):
        keyboard = None
        if text_button and url_button:
            keyboard = await self.get_keyboard(text_button, url_button)

        users_ids = await self.get_users()
        try:
            users_ids.remove(config.admin_id)
        except ValueError as e:
            pass

        count = 0
        try:
            for user_id in users_ids:
                if await self.send_message(int(user_id), from_chat_id, message_id, keyboard):
                    count+=1
                await asyncio.sleep(0.05)
        finally:
            logging.info(f"Разослал сообщение {count} пользователям")

        return count