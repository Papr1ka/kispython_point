<<<<<<< Updated upstream
from typing import Dict, Any, Union
=======
import asyncio
import re
from typing import Dict, Any, Union, Tuple
from logging import getLogger
>>>>>>> Stashed changes

import aiogram.types
from threading import Thread
from aiohttp import ClientSession, ClientConnectionError
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command, or_f
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bs4 import BeautifulSoup, NavigableString

from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Back, Select, Column
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram.types import ContentType, Message

from .db import UserData
from .middleware import AuthMiddleware

<<<<<<< Updated upstream
=======
template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>kispython_point</title>
</head>
<body>
    {}
</body>
</html>"""

logger = getLogger(__name__)

>>>>>>> Stashed changes

class CodeStates(StatesGroup):
    """
    Хранилище данных конечного автомата выбора задачи
    """
    #: Группа
    group = State()
    #: Номер задания, на 1 меньше фактического (индекс)
    task = State()
    #: Номер варианта
    variant = State()
    #: Код решения
    code = State()


groups = [f"ИВБО-{i:02}-22" for i in range(1, 10)]
groups += [f"ИКБО-{i:02}-22" for i in range(1, 37) if i not in [10, 24, 29, 34]]
groups += [f"ИМБО-{i:02}-22" for i in range(1, 3)]
groups += [f"ИНБО-{i:02}-22" for i in range(1, 13)]

tasks = [i for i in range(1, 13)]

variants = [i for i in range(1, 41)]


async def get_primary_data(*args, **kwargs):
    """
    Формирует данные для отображения в виждетах
    
    :return: Словарь с данными
    :rtype: Dict[str, List[str, ...]]
    """
    return {"groups": groups,
            "tasks": tasks,
            "variants": variants}


async def get_content(link: str):
    """
    Возвращает текст страницы с заданием или выбрасывает исключение,
    если страница не найдена
    
    :param link: Ссылка на страницу с заданием
    :type link: str
    :return: Текст страницы
    :rtype: str
    """
    async with ClientSession() as session:
        async with session.get(link) as page:
            assert page.status == 200
            text = await page.text('utf-8')
    return text


async def get_task_condition_html(link: str, variant: int) -> Union[str, None]:
    """Возвращает html код страницы с условием задачи варианта

    :param link: Ссылка на страницу с заданием
    :type link: str
    :param variant: Номер варианта
    :type variant: int
    :return: html код страницы или None
    :rtype: Union[str, None]
    """
    try:
        content = await get_content(link)
    except (AssertionError, ClientConnectionError):
        return

    parse = BeautifulSoup(content, "html.parser")
    tag = parse.find(name="h2", id=f"вариант-{variant}")
    next_variant = f"вариант-{variant + 1}"
    html = str(tag)

    def skip_br(tag):
        # Пропускает NavigableString "\n"
        if isinstance(tag, NavigableString):
            return tag.next_sibling
        return tag

    next_sibling = skip_br(tag.next_sibling)

    while next_sibling is not None and next_sibling.attrs.get('id') != next_variant:
        html += str(next_sibling)
        next_sibling = skip_br(next_sibling.next_sibling)
<<<<<<< Updated upstream
    return html
=======
    logger.info(f"Условие получено")
    return template.format(html)


async def format_code(code: str) -> Tuple[Union[str, None], int]:
    """
    Форматирует python-код в соответствии с PEP-8

    Возвращает отформатированный код и статус ответа:
    
    * Статус 200, код был отформатирован возвращает код
    * Статус 204, код был в соответствии с PEP-8 возвращает исходный код
    * Статус 400, синтаксическая ошибка возвращает None
    * Статус 500, иная ошибка (сервера) возвращает исходный код

    :param code: код программы
    :type code: str
    :return: отформатировнный код программы или None
    :rtype: Tuple[Union[str, None], int]
    """

    async with ClientSession() as session:
        try:
            logger.debug('Отправка кода на форматирование к black серверу')
            async with session.post("http://127.0.0.1:9090", data=code.encode('utf-8')) as response:
                logger.debug('Ответ от black', response.status)
                if response.status == 200:
                    text = await response.text('utf-8')
                    return text, response.status
                else:
                    return code, response.status
        except ClientConnectionError as E:
            logger.error('Не удалось подключиться к black серверу')
            return None, 404
>>>>>>> Stashed changes


async def on_group_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    """
    Обработчик события выбора группы
    """

    manager.dialog_data["group"] = item_id
<<<<<<< Updated upstream
    print("Group selected: ", item_id)
=======
    logger.info(f"Выбрана группа {item_id}")

    await manager.switch_to(CodeStates.variant)


async def on_variant_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    """
    Обработчик события выбора варианта задания
    """
    manager.dialog_data["variant"] = int(item_id)
    logger.info(f"Выбран вариант {item_id}")

>>>>>>> Stashed changes
    await manager.switch_to(CodeStates.task)


async def on_task_selected(callback: CallbackQuery, widget: Any,
                           manager: DialogManager, item_id: str):
    """
    Обработчик события выбора задания
    """
    manager.dialog_data["task"] = item_id
<<<<<<< Updated upstream
    print("Task selected: ", item_id)
    await manager.switch_to(CodeStates.variant)


async def on_variant_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    """
    Обработчик события выбора варианта задания
    """
    manager.dialog_data["variant"] = item_id
    print("Variant selected:", item_id)
    
=======
    logger.info(f"Выбрана Задача {item_id}")
>>>>>>> Stashed changes
    bot: Bot = manager._data.get('bot')
    chat_id = manager._data.get('event_chat').id

    data = manager.dialog_data
    condition_url = (
            f"https://kispython.ru/docs/{data['task']}/" +
            f"{groups[int(data['group'])]}.html#вариант-{data['variant']}"
    )

    manager.dialog_data['condition'] = condition_url
    file_name = f"{int(data['task']) + 1}_{groups[int(data['group'])]}_вариант-{data['variant']}.html"

    html = await get_task_condition_html(condition_url, data['variant'])
    if html is None:
        return await bot.send_message(chat_id, "К сожалению, условие не найдено")

    await bot.send_document(chat_id, BufferedInputFile(html.encode('utf-8'), file_name))
    await bot.send_message(chat_id, "Отправьте следующим сообщением Ваше решение выбранной задачи")
    await manager.switch_to(CodeStates.code)


async def expect_verdict(session: ClientSession, link: str):
    for _ in range(10):
        await asyncio.sleep(3)
        async with session.get(link) as page:
            if page.status != 200:
                break
            content = await page.read()
            parse = BeautifulSoup(content, "html.parser")
            if (status_tag := parse.find(name="div", attrs={"class": re.compile("^badge alert")})) is None:
                continue
            status = status_tag.text.strip()
            if "Отправлено" in status:
                continue
            msg_tag = parse.find(name="div", attrs={"class": "text-muted mb-2"})
            msg = msg_tag.text
            if msg_tag.parent.name == "form":
                msg = parse.find(name="div", attrs={"class": "callout callout-success"})
                msg = msg.find("div").text + "\n" + msg.find("small").text

            return status, msg
    status = "Произошла непредвиденная ошибка"
    return status, None


async def solve_handler(
        message: Message,
        message_input: MessageInput,
        manager: DialogManager):
    """
    Обработчик события отправления пользователем решения задачи
    """
    bot = message.bot
    user = message.from_user.id
    code = message.text

    if not (10 <= len(code) <= 10 ** 4):
        await message.reply("Код должен содержать от 10 до 10⁴ символов!")
        return

    group, variant, task = manager.dialog_data["group"], manager.dialog_data["variant"], manager.dialog_data["task"]
    user_session: ClientSession = manager.start_data["session"].session

    link = f"https://kispython.ru/group/{group}/variant/{int(variant) - 1}/task/{task}"

    async with user_session.get(link) as page:
        if page.status != 200:
            await message.reply("Произошла ошибка")
            return
        content = await page.read()
        parse = BeautifulSoup(content, "html.parser")
        csrf_tag = parse.find(name="input", attrs={"name": "csrf_token"})
        token = csrf_tag["value"]

    code, status = await format_code(code)
    if status == 200:
        await bot.send_message(user, "Ваш код был отформатирован в соответствии с требованиями pep-8")
    elif status == 204:
        await bot.send_message(user, "Ваш код соответствует формату pep-8, изменений не произведено")
    elif status == 400:
        await bot.send_message(user, "Ваш код содержит синтаксические ошибки, отправка решения отменена")
        return
    else:
        await bot.send_message(user,
                               "Произошла внутренняя ошибка. Проверка на соответствие формату pep-8 не выполнена")

    data = {
        "code": code,
        "csrf_token": token
    }
    async with user_session.post(link, data=data) as page:
        if page.status != 200:
            await message.reply("Произошла ошибка")
            return

    await bot.send_chat_action(message.chat.id, "typing")
    status, error = await expect_verdict(user_session, link)

    await bot.send_message(user, status)
    if error:
        await bot.send_message(user, error)


group = Window(
    Const("Выберите группу"),
    ScrollingGroup(
        Column(
            Select(
                Format("{item}"),
                items="groups",
                id="groups",
                item_id_getter=lambda x: groups.index(x),
                on_click=on_group_selected
            ),
        ),
        id="groups_a",
        width=1,
        height=10
    ),
    state=CodeStates.group
)
task = Window(
    Const("Выберите номер задачи"),
    ScrollingGroup(
        Column(
            Select(
                Format("{item}"),
                items="tasks",
                id="tasks",
                item_id_getter=lambda x: x - 1,
                on_click=on_task_selected
            ),
        ),
        id="tasks_a",
        width=3,
        height=4
    ),
    Back(text=Const("Назад")),
    state=CodeStates.task
)

variant = Window(
    Const("Выберите Ваш вариант"),
    ScrollingGroup(
        Column(
            Select(
                Format("{item}"),
                items="variants",
                id="variants",
                item_id_getter=lambda x: x,
                on_click=on_variant_selected
            ),
        ),
        id="variants_a",
        width=5,
        height=8
    ),
    Back(text=Const("Назад")),
    state=CodeStates.variant
)
task_display = Window(
    Format("Условие {dialog_data[condition]}"),
    Back(text=Const("Назад")),
    MessageInput(solve_handler, content_types=[ContentType.TEXT]),
    parse_mode="HTML",
    state=CodeStates.code
)

code_router = Router(name=__name__)

# Неавторизованные пользователи автоматом будут отфильтровываться
code_router.message.outer_middleware(AuthMiddleware())


# Далее можно считать, что работа идёт только с авторизованными

@code_router.message(or_f(Command("code"), F.text == "code"))
async def code_handler(message: Message, db: Dict[int, UserData], state: FSMContext, dialog_manager: DialogManager):
    """
    Обработчик команды code, входит в конечный автомат CodeStates
    """
<<<<<<< Updated upstream
=======
    logger.info(f"Команда code")

>>>>>>> Stashed changes
    await dialog_manager.start(CodeStates.group, mode=StartMode.RESET_STACK,
                               data={"session": db.get(message.from_user.id, None)})


dialog = Dialog(group, task, variant, task_display,
                getter=get_primary_data)
