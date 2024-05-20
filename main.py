import asyncio
import logging
import os
from typing import Dict

from aiogram.types import BotCommand, ErrorEvent
from aiogram_dialog import setup_dialogs
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from modules.auth import auth_router
from modules.code import code_router, dialog
from modules.db import UserData


FMT = "%(name)s : %(funcName)s : %(lineno)d : %(asctime)s : %(levelname)s : %(message)s"
DATE_FMT = "%d/%m/%Y %I:%M:%S %p"
logging.basicConfig(format=FMT, datefmt=DATE_FMT, level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv("./.env")
dp = Dispatcher()
API_TOKEN = os.getenv("BOT_TOKEN")


@dp.shutdown()
async def on_shutdown(db: Dict[int, UserData]):
    for value in db.values():
        session = value.session
        if session is not None and not session.closed:
            await session.close()



db = {}
commands = [
    BotCommand(command="auth", description="Авторизоваться через ЛКС МИРЭА"),
    BotCommand(command="code", description="Начать решать задачи"),
    BotCommand(command="quit", description="Выйти из ЛКС МИРЭА"),
    BotCommand(command="test", description="Тест"),
]


async def main():
    bot = Bot(token=API_TOKEN)
    await bot.set_my_commands(commands=commands)
    dp.include_routers(auth_router, code_router, dialog)
    setup_dialogs(dp)
    await dp.start_polling(bot, db=db)


@dp.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Критическая ошибка вызвана %s", event.exception, exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
