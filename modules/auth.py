import logging

from aiogram import Router, Bot, F
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiohttp import ClientSession

from .login import AuthStatus, prepare_session_for_login, login_via_lks
from .db import UserData

from typing import Dict
from aiogram.utils.keyboard import ReplyKeyboardBuilder

auth_router = Router(name=__name__)


class AuthData(StatesGroup):
    login_password = State()


@auth_router.message(Command("auth"))
async def start_handler(message: Message, state: FSMContext):
    await state.set_state(AuthData.login_password)
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="cancel"))
    message = await message.answer(
        f"""Привет, {message.from_user.full_name}!
Введи пару <login>:<password> от ЛКС МИРЭА""", reply_markup=builder.as_markup(resize_keyboard=True))


@auth_router.message(or_f(Command("cancel"), F.text == "cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    curr_state = await state.get_state()
    if curr_state is None:
        return

    await state.clear()
    await message.answer("Отменено.", reply_markup=ReplyKeyboardRemove())


def hide_value(value: str, n: int = 2):
    if len(value) < 2 * n:
        return value[1] + "*" * (len(value) - 1)
    return value[:n] + "*" * (len(value) - 2 * n) + value[-n:]


@auth_router.message(AuthData.login_password, F.text)
async def login_handler(message: Message, bot: Bot, state: FSMContext, db: Dict[int, UserData]):
    pair = message.text.split(":")
    if len(pair) != 2:
        return await message.answer("Введите в формате <login>:<password>")

    login, password = pair

    if len(login) < 6 or len(password) < 6:
        return await message.answer("Введите корректные данные <login>:<password>")

    reply_message = f"Логин: {login}, Пароль: {hide_value(password)}"

    await bot.send_chat_action(message.chat.id, "typing")

    user_id = message.from_user.id
    user_data = db.get(user_id, None)

    if user_data is None or user_data.session_data is None:
        session = ClientSession()
        status, session_data = await prepare_session_for_login(session)
        if status != AuthStatus.SUCCESS:
            return await message.answer(status.get_message())  # Если сервер недоступен или что-то поменялось
        user_data = UserData(False, 0, session, session_data)
        db[user_id] = user_data

    status = await login_via_lks(user_data.session, login, password, user_data.session_data)
    if status != AuthStatus.SUCCESS:
        reply_message += f"\nСтатус: {status.get_message()}\nПопробуйте ещё раз"
        await message.answer(reply_message)
        if status == AuthStatus.SERVER_UNAVAILABLE:
            return
    else:
        await message.reply("Авторизация прошла успешно\nПора решать задачи /code")
        db[user_id].authorized = True
        await state.clear()


@auth_router.message(Command("quit"))
async def quit_handler(message: Message, state: FSMContext, db: Dict[int, UserData]):
    user_id = message.from_user.id

    if db.get(user_id, None) is None or db[user_id].authorized is False:
        await message.reply("Вы ещё не прошли авторизацию в системе")

    await db[user_id].session.close()
    db.pop(user_id)
    await state.clear()
    await message.reply("Выполнен выход из профиля")


@auth_router.message(AuthData.login_password)
async def login_handler(message: Message, bot: Bot, state: FSMContext, db: Dict[int, UserData]):
    """
    Обработка нетекстового ввода
    """
    await message.answer("Введите корректные данные <login>:<password>")
