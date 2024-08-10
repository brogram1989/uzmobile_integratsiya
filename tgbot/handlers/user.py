from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from tgbot.keyboards.inline import MainMenu, MenuStat
from .admin import is_admin, is_user
user_router = Router()

#bosh menu handleri
@user_router.message(CommandStart())
@user_router.message(Command("menu"))
async def user_start(message: Message):
    await message.answer("Bosh menu", reply_markup=MainMenu)
#bosh menuga qaytish handleri
@user_router.callback_query(F.data == "menu")
async def call_back_menu(query: CallbackQuery):
    await query.answer()
    await query.message.edit_text("Bosh menu", reply_markup=MainMenu)


@user_router.callback_query(F.data == "statistika")
async def call_back_menu(query: CallbackQuery):
    if is_user(query.from_user.id):
         await query.answer()
         await query.message.edit_text("Statistika bo'limi", reply_markup=MenuStat)
    else:
        await query.answer()
        await query.message.answer("🚫Siz foydalanuvchi emassiz!", reply_markup=ReplyKeyboardRemove())