from core.utils.config import config
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault


async def set_commands(bot: Bot):
    user_commands = [
        BotCommand(
            command="start",
            description="Вывести посты"
        )
    ]

    admin_commands = user_commands + [BotCommand(command="ad", description='Сделать рекламный пост')]

    await bot.set_my_commands(admin_commands, BotCommandScopeChat(chat_id=config.admin_id))
    await bot.set_my_commands(user_commands, BotCommandScopeDefault())