from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BotCommand
from aiogram.utils.formatting import as_section, as_key_value, as_marked_list

menu_router = Router()



@menu_router.message(Command("about"))
async def help_command(message: Message):
    await message.answer("This is the help desk. Choose an option:"
                         "\n/start - bot ishini boshlash"
                        "\n/about - xaqida "
                         "\n\n⌨️💻bu bot Uzmobile filiali, TRD, Integratsiya otdeli boti"
                         "\ncontacts:"
                         "\ntelegram: t.me/Gafurov_Dilshod"
                         "\nGitHub: https://github.com/brogram1989/"
                         )

#_________________________________________________________________________#


