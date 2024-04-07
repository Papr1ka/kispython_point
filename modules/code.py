from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import operator

from .db import UserData
from .middleware import AuthMiddleware
from typing import Dict, Any

from aiogram.filters.state import State, StatesGroup

from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup
from aiogram_dialog.widgets.text import Const, List, Format

from aiogram_dialog.widgets.kbd import Select, Column

class CodeStates(StatesGroup):
    group = State()
    task = State()
    code = State()


groups = [f"ИВБО-{i:02}-22" for i in range(1, 10)]
groups += [f"ИКБО-{i:02}-22" for i in range(1, 37) if i not in [10, 24, 29, 34]]
groups += [f"ИМБО-{i:02}-22" for i in range(1, 3)]
groups += [f"ИНБО-{i:02}-22" for i in range(1, 13)]

async def get_groups(*args, **kwargs):
    return {"groups": groups}

async def on_group_selected(callback: CallbackQuery, widget: Any,
                            manager: DialogManager, item_id: str):
    print("Fruit selected: ", item_id)

group = Window(
    Const("Выберите группу"),
    ScrollingGroup(
        Column(
            Select(
                Format("{item}"),
                items="groups",
                id="groups",
                item_id_getter=lambda x: x,
                on_click=on_group_selected
            ),
        ),
        id="groups_a",
        width=1,
        height=10
    ),
    getter=get_groups,
    state=CodeStates.group
)

code_router = Router(name=__name__)

# Неавторизованные пользователи автоматом будут отфильтровываться
# code_router.message.outer_middleware(AuthMiddleware())
# Далее можно считать, что работа идёт только с авторизованными


@code_router.message(or_f(Command("code"), F.text == "code"))
async def code_handler(message: Message, db: Dict[int, UserData], state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.start(CodeStates.group, mode=StartMode.RESET_STACK)

dialog = Dialog(group)
