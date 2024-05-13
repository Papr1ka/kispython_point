from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup, NavigableString
from aiogram.fsm.state import State, StatesGroup
from .db import UserData
from .middleware import AuthMiddleware
from typing import Dict, Any

from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Back
from aiogram_dialog.widgets.text import Const, Format

from aiogram_dialog.widgets.kbd import Select, Column
import requests

from aiogram.types import BufferedInputFile
from aiogram import Bot

from aiohttp import ClientSession


class CodeStates(StatesGroup):
    group = State()
    task = State()
    variant = State()
    code = State()


groups = [f"ИВБО-{i:02}-22" for i in range(1, 10)]
groups += [f"ИКБО-{i:02}-22" for i in range(1, 37) if i not in [10, 24, 29, 34]]
groups += [f"ИМБО-{i:02}-22" for i in range(1, 3)]
groups += [f"ИНБО-{i:02}-22" for i in range(1, 13)]

tasks = [i for i in range(1, 13)]

variants = [i for i in range(1, 41)]


async def get_primary_data(*args, **kwargs):
    return {"groups": groups,
            "tasks": tasks,
            "variants": variants}


async def get_content(link):
    async with ClientSession() as session:
        async with session.get(link) as page:
            assert page.status == 200
            text = await page.text('utf-8')
    return text


async def get_task_condition(manager: DialogManager):  # TODO: сделать устойчивость к плохим request'ам
    data = manager.dialog_data
    link = f"https://kispython.ru/docs/{data['task']}/{groups[int(data['group'])]}.html"
    bot = manager._data.get('bot')
    chat_id = manager._data.get('event_chat').id
    flag = False
    content = None
    try:
        content = await get_content(link)
    except Exception as E:
        flag = True

    if content is None or len(content) == 0 or flag:
        return await bot.send_message(chat_id, "Ошибка при парсинге сайта")

    parse = BeautifulSoup(content, "html.parser")
    tag = parse.find(name="h2", id=f"вариант-{data['variant']}")
    next_variant = f"вариант-{int(data['variant']) + 1}"
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

    file_name = f"{data['task']}_{groups[int(data['group'])]}_вариант-{data['variant']}.html"

    await bot.send_document(chat_id, BufferedInputFile(html.encode('utf-8'), file_name))


async def on_group_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    
    manager.dialog_data["group"] = item_id
    print("Group selected: ", item_id)
    await manager.switch_to(CodeStates.task)


async def on_task_selected(callback: CallbackQuery, widget: Any,
                           manager: DialogManager, item_id: str):
    manager.dialog_data["task"] = item_id
    print("Task selected: ", item_id)
    await manager.switch_to(CodeStates.variant)


async def on_variant_selected(callback: CallbackQuery, widget: Any,
                              manager: DialogManager, item_id: str):
    manager.dialog_data["variant"] = item_id
    print("Variant selected:", item_id)
    data = manager.dialog_data
    condifion_url = (f"https://kispython.ru/docs/{data['task']}/" +
    f"{groups[int(data['group'])]}.html#вариант-{int(data['variant'])}")
    manager.dialog_data['condition'] = condifion_url
    await get_task_condition(manager)
    await manager.switch_to(CodeStates.code)

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
    parse_mode="HTML",
    state=CodeStates.code
)

code_router = Router(name=__name__)


# Неавторизованные пользователи автоматом будут отфильтровываться
# code_router.message.outer_middleware(AuthMiddleware())
# Далее можно считать, что работа идёт только с авторизованными

@code_router.message(Command("test"))
async def send_pdf(message: Message, bot: Bot):
    link = f"https://kispython.ru/docs/11/ИКБО-04-22.html"
    content = requests.get(link)
    content.encoding = "utf-8"

    parse = BeautifulSoup(content.text, "html.parser")
    tag = parse.find(name="h2", id=f"вариант-{11}")
    next_variant = f"вариант-{12}"
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

    with open("out.html", "w") as file:
        file.write(html)
    
    await message.reply_document(BufferedInputFile(html.encode('utf-8'), 'test.html'))


@code_router.message(or_f(Command("code"), F.text == "code"))
async def code_handler(message: Message, db: Dict[int, UserData], state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(CodeStates.group, mode=StartMode.RESET_STACK,
                               data={"session": db.get(message.from_user.id, None)})


dialog = Dialog(group, task, variant, task_display,
                getter=get_primary_data)
