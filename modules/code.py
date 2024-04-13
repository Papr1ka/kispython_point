from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup
from aiogram.fsm.state import State, StatesGroup
import operator
from aiogram_dialog.widgets.text import Jinja
from .db import UserData
from .middleware import AuthMiddleware
from typing import Dict, Any

from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup
from aiogram_dialog.widgets.text import Const, List, Format

from aiogram_dialog.widgets.kbd import Select, Column

import requests


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


async def get_task_condition(manager: DialogManager):  # TODO: сделать устойчивость к плохим request'ам
    data = manager.dialog_data
    link = f"https://kispython.ru/docs/{data['task']}/{groups[int(data['group'])]}.html"
    content = requests.get(link)
    content.encoding = "utf-8"

    parse = BeautifulSoup(content.text, "html.parser")
    tag = parse.find(name="h2", id=f"вариант-{data['variant']}")
    html = str(tag)
    for i in range(5):
        tag = tag.find_next_sibling()
        html += str(tag)
    manager.dialog_data["condition"] = html

    print(manager.dialog_data["condition"])


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
                item_id_getter=lambda x: x - 1,
                on_click=on_variant_selected
            ),
        ),
        id="variants_a",
        width=5,
        height=8
    ),
    state=CodeStates.variant
)
task_display = Window(
    Format("{dialog_data[condition]}"),
    parse_mode="HTML",
    state=CodeStates.code
)

code_router = Router(name=__name__)


# Неавторизованные пользователи автоматом будут отфильтровываться
# code_router.message.outer_middleware(AuthMiddleware())
# Далее можно считать, что работа идёт только с авторизованными


@code_router.message(or_f(Command("code"), F.text == "code"))
async def code_handler(message: Message, db: Dict[int, UserData], state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(CodeStates.group, mode=StartMode.RESET_STACK,
                               data={"session": db.get(message.from_user.id, None)})


dialog = Dialog(group, task, variant, task_display,
                getter=get_primary_data)
