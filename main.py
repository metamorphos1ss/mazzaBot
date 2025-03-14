import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command

from core.handlers.basic import get_start, userdb_init
from core.utils.ad_list import AdList
from core.utils.ad_state import Steps
from core.utils.config import config
from core.utils.commands import set_commands
from core.middleware.dbMiddleware import DbSession
from core.handlers import ad

async def start_bot(bot: Bot):
    await set_commands(bot)
    logging.info('БОТ ЗАПУЩЕН')


async def create_pool():
    return await asyncpg.create_pool(user=config.db_user, password=config.db_password, database=config.db_name,
                              host=config.db_host, port=config.db_port, command_timeout=60)

async def start():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')
    bot = Bot(token=config.token)
    pool_connect = await create_pool()
    dp = Dispatcher()
    dp.update.middleware.register(DbSession(pool_connect))
    dp.message.register(ad.get_ad, Command('ad'), F.chat.id == config.admin_id)
    dp.message.register(ad.get_message, Steps.get_message, F.chat.id == config.admin_id)
    dp.callback_query.register(ad.button, Steps.button)
    dp.message.register(ad.get_text_button, Steps.get_text_button)
    dp.message.register(ad.get_url_button, Steps.get_url_button)
    dp.callback_query.register(ad.ad_decide, F.data.in_(['confirm_ad', 'cancel_ad']))
    ad_list = AdList(bot, pool_connect)

    dp.message.register(get_start, Command('start'))
    dp.startup.register(start_bot)

    dp.message.register(userdb_init)

    try:
        await dp.start_polling(bot, adlist=ad_list)
    except Exception as e:
        logging.error(f"[!!! Exception !!!] - {e}", exc_info=True)
    finally:
        await bot.session.close()
if __name__ == '__main__':
    asyncio.run(start())