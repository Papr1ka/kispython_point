from enum import Enum
from typing import Dict, Union

from aiohttp import ClientSession
from aiohttp import ClientConnectionError
from bs4 import BeautifulSoup


AUTH_URL = "https://kispython.ru/login/lks"


class AuthStatus(Enum):   
    """
    Статус результата авторизации
    """
    SERVER_UNAVAILABLE = 0, "Сервер недоступен, попробуйте позже"
    INVALID_AUTH_DATA = 1, "Неверные данные для авторизации"
    TOO_MANY_ATTEMPTS = 2, "Слишком много неудачных попыток"
    SUCCESS = 3, "Успешно"
    UNDEFINED_ERROR = 4, "Ошибка"

    def get_message(self):
        """Возвращает строковое обозначение ошибки

        :return: Строка с обозначением ошибки
        :rtype: str
        """
        return self.value[1]


async def prepare_session_for_login(session: ClientSession) -> AuthStatus:
    """Подготавливает ссылки и csrf_token для будущей авторизации

    :param session: объект сессии
    :type session: ClientSession
    :return: Cтатус ответа
    :rtype: AuthStatus
    """
    try:
        async with session.get(AUTH_URL, headers={"Referer": "https://kispython.ru/"}) as page:
            if page.status != 200:
                return AuthStatus.SERVER_UNAVAILABLE, None

            content = await page.read()
            log_url = str(page.url)
            parse = BeautifulSoup(content, "html.parser")
            csrf_tag = parse.find(name="input", attrs={"name": "csrfmiddlewaretoken"})  # CSRF код
            token = csrf_tag["value"]
            next_tag = parse.find(name="input", attrs={"name": "next"})  # адрес следующего редиректа
            next_url = next_tag["value"]
            return AuthStatus.SUCCESS, {
                "log_url": log_url,
                "csrfmiddlewaretoken": token,
                "next": next_url
            }
    except ClientConnectionError as E:
        return AuthStatus.SERVER_UNAVAILABLE, None


async def login_via_lks(session: ClientSession, login: str, password: str, data: Dict[str, str]) -> AuthStatus:
    """Авторизует пользователя с парой login, password, все токены записываются в session

    :param session: объект сессии
    :type session: ClientSession
    :param login: логин пользователя
    :type login: str
    :param password: пароль пользователя
    :type password: str
    :param data: Словарь, возвращаемый prepare_session_for_login
    :type data: Dict[str, str]
    :return: Cтатус ответа
    :rtype: AuthStatus
    """

    data = data.copy()
    data.update(login=login, password=password)
    log_url = data.pop("log_url")
    try:
        async with session.post(log_url, data=data, headers={"Referer": log_url}) as page:
            if page.status != 200:
                return AuthStatus.SERVER_UNAVAILABLE

            content = await page.read()
            parse = BeautifulSoup(content, "html.parser")
            login_form = parse.find(id="mirea-users-loginform")
            if login_form is not None and login_form.text.startswith("Указан неверный логин/пароль"):
                return AuthStatus.INVALID_AUTH_DATA
            elif login_form is not None and login_form.text.startswith("Превышено количество неудачных попыток входа"):
                return AuthStatus.TOO_MANY_ATTEMPTS
            elif login_form is not None:
                return AuthStatus.UNDEFINED_ERROR
            return AuthStatus.SUCCESS
    except ClientConnectionError as E:
        return AuthStatus.SERVER_UNAVAILABLE


async def parse_tasks(session: ClientSession) -> Union[int, None]:
    """Возвращает количество существующих задач, доступных к решению или None,
    объект сессии может быть любым

    :param session: Объект сесси
    :type session: ClientSession
    :return: Количество ошибок или None
    :rtype: Union[int, None]
    """    
    try:
        async with session.get("https://kispython.ru/group/0") as page:
            content = await page.read()
            parse = BeautifulSoup(content, "html.parser")
            login_form = parse.find(name="table")
            if login_form is None:
                return None
            tr = login_form.find(name="thead").find("tr")
            numbers = tr.find_all(name="a")
            return len(numbers)
    except ClientConnectionError as E:
        return None
