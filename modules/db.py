from dataclasses import dataclass
from aiohttp import ClientSession


@dataclass
class UserData:
    """
    Объект данных, связанных с пользователем в кэше
    """
    authorized: bool #: Авторизован ли пользователь
    passes: int #: Кол-во попыток решения задачи
    session: ClientSession #: Объект сессии с токенами для авторизации
    session_data: dict #: Данные для авторизации (передаётся в login_via_lks)
