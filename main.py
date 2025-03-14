import asyncio
from functools import partial
import logging
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage

from core.handlers.basic import get_start, userdb_init
from core.utils.ad_list import AdList
from core.utils.ad_state import Steps
from core.utils.commands_state import Commands
from core.utils.dbconnect import Request
from core.utils.config import config
from core.utils.commands import set_commands
from core.middleware.dbMiddleware import DbSession
from core.handlers import ad, info

bot = Bot(token=config.token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def start_bot(bot: Bot, req: Request):
    await set_commands(bot)
    await req.bot_messages_init()

    start_text = await req.get_start_text()

    storage_key = StorageKey(chat_id=-1, user_id=-1, bot_id=bot.id)

    await dp.storage.set_data(key=storage_key, data={"start_text": start_text})


async def create_pool():
    return await asyncpg.create_pool(user=config.db_user, password=config.db_password, database=config.db_name,
                              host=config.db_host, port=config.db_port, command_timeout=60)

async def start():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
    pool_connect = await create_pool()
    req=Request(pool_connect)
    dp.update.middleware.register(DbSession(pool_connect))


    dp.message.register(ad.get_ad, Command('ad'), F.chat.id == config.admin_id)
    dp.message.register(ad.get_message, Steps.get_message, F.chat.id == config.admin_id)
    dp.callback_query.register(ad.button, Steps.button)
    dp.message.register(ad.get_text_button, Steps.get_text_button)
    dp.message.register(ad.get_url_button, Steps.get_url_button)
    dp.callback_query.register(ad.ad_decide, F.data.in_(['confirm_ad', 'cancel_ad']))
    ad_list = AdList(bot, pool_connect)

    dp.message.register(info.get_command, Command('commands'), F.chat.id == config.admin_id)
    dp.message.register(info.get_command_message, Commands.get_command, F.chat.id == config.admin_id)
    dp.message.register(info.get_text, Commands.get_text, F.chat.id == config.admin_id)
    dp.callback_query.register(info.cmd_decide, F.data.in_(['confirm_cmd', 'cancel_cmd']))


    dp.message.register(partial(get_start, storage=dp.storage), Command('start'))
    dp.message.register(start_bot, Command('reload_commands'), F.chat.id == config.admin_id)
    dp.startup.register(partial(start_bot, bot=bot, req=req))

    dp.message.register(userdb_init)

    try:
        await dp.start_polling(bot, adlist=ad_list)
    except Exception as e:
        logging.error(f"[!!! Exception !!!] - {e}", exc_info=True)
    finally:
        await bot.session.close()
if __name__ == '__main__':
    asyncio.run(start())