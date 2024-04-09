from dataclasses import dataclass
from aiohttp import ClientSession


@dataclass
class UserData:
    authorized: bool  # Авторизован ли пользователь
    passes: int  # Кол-во попыток решения задачи
    session: ClientSession  # Объект сессии со всеми токенами
    session_data: dict  # Для авторизации (передаётся в login_via_lks)
