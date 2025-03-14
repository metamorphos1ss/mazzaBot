import logging
import asyncpg
from asyncpg import Record

from core.utils.config import config


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    async def add_data(self, user_id, user_name):
        query = f"CREATE TABLE IF NOT EXISTS users (user_id bigint, user_name text, PRIMARY KEY (user_id));"
        await self.connector.execute(query)
        if user_id != config.admin_id:
            query = f"INSERT INTO users (user_id, user_name) VALUES ({user_id}, '{user_name}') " \
                    f"ON CONFLICT (user_id) DO UPDATE SET user_name='{user_name}'"
            await self.connector.execute(query)

    async def check_table(self):
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users_ad');"
        result = await self.connector.fetchval(query)
        logging.info(f'check_table result: {result}')
        return result

    async def create_table(self):
        query = f"CREATE TABLE users_ad (user_id bigint NOT NULL, status text, PRIMARY KEY (user_id));"
        await self.connector.execute(query)
        query = f"INSERT INTO users_ad (user_id, status) SELECT user_id, 'waiting' FROM users"
        await self.connector.execute(query)


    async def delete_table(self):
        query = f"DROP TABLE users_ad;"
        await self.connector.execute(query)


    async def bot_messages_init(self):
        logging.info('я хотя бы вызываюсь')
        query = f"CREATE TABLE IF NOT EXISTS bot_messages (id SERIAL PRIMARY KEY, command TEXT NOT NULL UNIQUE, message TEXT NOT NULL);"
        await self.connector.execute(query)

        query = """
    INSERT INTO bot_messages (command, message)
    VALUES ('/start', 'priv')
    ON CONFLICT (command) DO NOTHING;
    """
        await self.connector.execute(query)

    async def bot_messages_update(self, command: str, text: str):
        logging.info(f'обновляю команду {command}')
        query = query = """
            INSERT INTO bot_messages (command, message) 
            VALUES ($1, $2)
            ON CONFLICT (command) DO UPDATE SET message = EXCLUDED.message;
    """
        await self.connector.execute(query, command, text)


#TODO переименовать эту переменную
    async def get_start_text(self):
        query = "SELECT message FROM bot_messages WHERE command='/start';"
        result = await self.connector.fetchval(query)
        return result if result else "default text"