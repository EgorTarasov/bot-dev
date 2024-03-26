"""
- coworking
- profile

"""

from sys import prefix
import typing as tp
import asyncio

from aiogram import types, Router, F

from aiogram.filters import CommandStart, Command, or_f
from aiogram.filters.command import CommandObject
from aiogram.utils.markdown import hbold
from aiogram.utils.i18n import gettext as _
from bot.settings import Settings

from repositories.users.base import UserRepositoryBase

from ..keyboards.menu import menu_keyboard, base_menu_reply_key, MainMenuCallback

from repositories.users.models import TelegramUser


router: tp.Final[Router] = Router(name="common")


@router.message(CommandStart())
async def command_start_handler(
    message: types.Message,
    command: CommandObject,
    tg_user: TelegramUser,
    settings: Settings,
    user_repo: UserRepositoryBase,
) -> None:
    if command.args:
        code = command.args
        try:
            if code != "broadcast":
                user_repo.use_invite_code(code, tg_user.tg_id)
                await message.answer(
                    _(
                        """Вы получили права админисратора
    почти в каждом разделе бота есть меню администратора, которое открывает функции по управлению разделом"""
                    )
                )
        except Exception as e:
            await message.answer(_("""Упс, что-то пошло не так"""))

    if message.from_user is None:
        return

    username = hbold(tg_user.username or tg_user.first_name)
    await message.answer(
        text=_("Hello , {username}!").format(username=username),
        reply_markup=base_menu_reply_key(),
    )
    await asyncio.sleep(0.2)
    await message.answer(
        text = _("Текст главного меню"),
        reply_markup=menu_keyboard()
    )

#handle menu via replyKeyboard
@router.message(F.text == "🏠 Главное меню")
async def menu_handler(message: types.Message) -> None:
    await message.answer(
        text=_("Текст главного меню"),
        reply_markup=menu_keyboard(),
    )


@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "menu"))
async def menu_callbacks(callback: types.CallbackQuery) -> None:
    msg_text = _("Текст главного меню")
    markup = menu_keyboard()
    if not callback.message:
        await callback.answer(
            text=msg_text,
            reply_markup=markup,
        )
    else:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()


@router.callback_query(MainMenuCallback.filter(F.next_menu_prefix == "help"))
async def help_callbacks(callback: types.CallbackQuery) -> None:
    msg_text = _("""Текст помощи на /help для главного меню""")
    markup = menu_keyboard()
    if not callback.message:
        await callback.answer(
            text=msg_text,
            reply_markup=markup,
        )
    else:
        await callback.message.edit_text(msg_text, reply_markup=markup)
        await callback.answer()


@router.message(Command("help", prefix="/"))
async def help_handler(message: types.Message) -> None:
    await message.answer(
        _("""Текст помощи на /help для главного меню"""),
        reply_markup=menu_keyboard(),
    )
