import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from modules.auth import auth_router
from modules.code import code_router, dialog
from modules.db import UserData
from typing import Dict

from aiogram.types import BotCommand
from aiogram.methods.set_my_commands import SetMyCommands
from aiogram_dialog import setup_dialogs

dp = Dispatcher()


@dp.shutdown()
async def on_shutdown(db: Dict[int, UserData]):
    for value in db.values():
        session = value.session
        if session is not None and not session.closed:
            await session.close()

API_TOKEN = os.getenv("BOT_TOKEN")
db = {}

commands = [
    BotCommand(command="auth", description="Авторизоваться через ЛКС МИРЭА"),
    BotCommand(command="code", description="Начать решать задачи")
]



async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=API_TOKEN)
    await bot.set_my_commands(commands=commands)
    dp.include_routers(auth_router, code_router, dialog)
    setup_dialogs(dp)
    await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    asyncio.run(main())
