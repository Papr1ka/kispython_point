from typing import Callable, Dict, Any, Awaitable
from logging import getLogger

from aiogram import BaseMiddleware
from aiogram.types import Message

from .db import UserData


logger = getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    При включении в маршрутизатор гарантирует,
    что команда будет обработана только если пользователь авторизован
    """
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, UserData], Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        db: Dict[int, UserData] = data.get("db")
        assert db is not None, "Забыли передать db в bot.start_pooling в main"
        user_id = message.from_user.id
        user_data = db.get(user_id)
        if user_data is None or user_data.authorized is False:
            logger.info("Вызов команды без авторизации")            
            return await message.answer("Для этого авторизуйтесь через /auth")
        return await handler(message, data)
