from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from tgbot.keyboards.inline import AdminMenu, user_menu, FileMenu
from tgbot.filters.admin import AdminFilter
from tgbot.config import ADMINS, USERS
from tgbot.states.bot_states import AdminCommands
admin_router = Router()
admin_router.message.filter(AdminFilter())
#______________________________________________________________________#
def is_admin(user_id: int):
    return user_id in ADMINS

def is_user(user_id: int):
    return user_id in USERS
def add_user(user_id: int ):
    if user_id not in USERS:
        USERS.append(user_id)
        return f"{user_id} raqalmi foydalanuvchi muvaffaqqiyatli qo'shildi"
    else:
        return f"{user_id} raqamli foydalanuvchi yo'q"

def del_user(user_id: int ):
    if user_id in USERS:
        USERS.remove(user_id)
        return f"{user_id} raqamli foydalanuvchilar ro'yxatidan chiqazildi"
    else:
        return f"{user_id} raqamli foydalanuvchi yo'q"

def set_admin(user_id: int ):
    if user_id not in ADMINS:
        ADMINS.append(user_id)
        return f"{user_id} raqamli foydalanuvchi admin sifatida qo'shildi"
    else:
        return f"{user_id} raqamli foydalanuvchi yo'q"

def remove_admin(user_id: int ):
    if user_id in ADMINS:
        ADMINS.remove(user_id)
        return f"{user_id} raqamli foydalanuvchi adminlar ro'yxatidan chiqazildi"
    else:
        return f"{user_id} raqamli admin yo'q"

#______________________________________________________________________#

@admin_router.callback_query(F.data == "admin_commands")
async def admin_command(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to remove admin privileges from a user here
        await query.answer()
        await query.message.edit_text("Admin buyruqlari bo'limi", reply_markup=AdminMenu)
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")
        await query.message.answer("Siz admin emasiz")
#_______________________________________________________________________________________________________#
@admin_router.callback_query(F.data == "menu_users")
async def admin_command(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to remove admin privileges from a user here
        await query.answer()
        await query.message.edit_text("Foydalanuvchilar bilan ishlash bo'limi", reply_markup=user_menu)
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")

#menu usersda foydalanuvchi qo'shish, o'chirish , admin qilish uchun handlerlar

@admin_router.callback_query(F.data == "add_user")
async def admin_check(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        await query.answer()
        await query.answer("yangi foydalanuvchi ID sini kirgazing")
        await query.message.answer("Foydalanuvchi 🆔 sini aniqlash uchun https://t.me/username_to_id_bot dan foydalanishingiz mumkun")
        await state.set_state(AdminCommands.user_id)
    else:
        await query.answer()
        await query.answer("Sizda foydalanuvchi qo'shish xuquqi mavjud emas")


#admin kirgizadigan useridni USERS listga yozish uchun handler

@admin_router.message(AdminCommands.user_id)
async def new_users_id(message: Message, state:FSMContext):
    try:
        # Get the comment from the message
        new_user = message.text
        new_user = int(new_user)
        add_user(new_user)
        await message.answer(f"siz id={new_user} foydalanuvchini bazaga kiritdingiz!\nBazada {len(USERS)} ta foydalanuvchi bor")
        # Finish the state
        await state.clear()
    except Exception as e:
        await message.reply(f"❌❓Xatolik yuzaga keldi: <b>{str(e)}</b>\n"
                            f"qaytadan urinib ko'ring!")
        await state.clear()

@admin_router.callback_query(F.data == "list_users")
async def list_users(query: CallbackQuery):
    if is_admin(query.from_user.id):
        # Your logic to delete a user here
        await query.answer()
        await query.answer("Foydalanuvchilar ro'yxati")
        await query.message.edit_text(f"Bazada {len(USERS)} ta 👤 foydalanuvchi bor.\nFoydalanuvchilar ro'yxati\n"
                                            f"{USERS}")
        await query.message.answer(f"Bazada {len(ADMINS)} ta 🥷 admin bor.\nAdminlar ro'yxati\n{ADMINS}")
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")



@admin_router.callback_query(F.data == "del_user")
async def delete_user(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to delete a user here
        await query.answer()
        await query.answer("O'chirmoqcvhi bo'lgan foydalanuvchi ID sini kirgazing")
        await query.message.answer("Foydalanuvchini o'chirish, uning 🆔 sini kiriting. \n"
                                            "<code>🆔 faqatgina raqamlardan iborat ketma ketligdagi son</code>")
        await state.set_state(AdminCommands.del_user)
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")



# #admin kirgizadigan useridni USERS listdan o'chirish uchun handler

@admin_router.message(AdminCommands.del_user)
async def del_users(message: Message, state:FSMContext):
    try:
        # Get the comment from the message
        user_id = message.text
        user_id = int(user_id)
        del_user(user_id)
        await message.answer(f"id={user_id} foydalanuvchi bazadan o'chirildi!\nBazada {len(USERS)} ta foydalanuvchi qoldi!")
        # Finish the state
        await state.clear()
    except Exception as e:
        await message.reply(f"❌❓Xatolik yuzaga keldi: <b>{str(e)}</b>\n"
                            f"qaytadan urinib ko'ring!")
        await state.clear()


@admin_router.callback_query(F.data == "set_admin")
async def set_new_admin(query: CallbackQuery, state:FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to set a user as admin here
        await query.answer()
        await query.answer("admin qilmoqchi bo'lgan foydalanuvchini ID sini kirgazing")
        await query.message.answer("Foydalanuvchini admin qilish uchun, uning 🆔 sini kiriting. \n"
                                    "<code>🆔 faqatgina raqamlardan iborat ketma ketligdagi son</code>")
        await state.set_state(AdminCommands.set_admin)
    else:
        await query.answer()
        await query.answer("Sizda foydalanuvchi admin qilib belgilash xuquqi mavjud emas")

@admin_router.message(AdminCommands.set_admin)
async def new_admin(message: Message, state:FSMContext):
    try:
        # Get the comment from the message
        admin = message.text
        admin = int(admin)
        add_user(admin)
        set_admin(admin)
        await message.answer(f"siz id={admin} foydalanuvchini admin qilib belgiladingiz!\nBazada {len(ADMINS)} ta admin bor")
        # Finish the state
        await state.clear()
    except Exception as e:
        await message.reply(f"❌❓Xatolik yuzaga keldi: <b>{str(e)}</b>\n"
                            f"qaytadan urinib ko'ring!")
        await state.clear()

@admin_router.callback_query(F.data == "del_admin")
async def delete_admin(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        await query.answer()
        # Your logic to remove admin privileges from a user here
        await query.answer("userni adminlikdan chiqarish")
        await query.message.answer("Foydalanuvchini adminlar ro'yxatidan o'chirish uchun, uning 🆔 sini kiriting. \n"
                                            "<code>🆔 faqatgina raqamlardan iborat ketma ketligdagi son</code>")
        await state.set_state(AdminCommands.del_admin)
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")


# #admin kirgizadigan useridni ADMINS listdan o'chirish uchun handler

@admin_router.message(AdminCommands.del_admin)
async def del_admin(message: Message, state:FSMContext):
    try:
        # Get the comment from the message
        user_id = message.text
        user_id = int(user_id)
        remove_admin(user_id)
        await message.answer(f"id={user_id} admin bazadan o'chirildi!\nBazada {len(ADMINS)} ta admin qoldi!")
        # Finish the state
        await state.clear()
    except Exception as e:
        await message.reply(f"❌❓Xatolik yuzaga keldi: <b>{str(e)}</b>\n"
                            f"qaytadan urinib ko'ring!")
        await state.clear()
#______________________________________________________________________#
#fayllarni yuklash menusi

@admin_router.callback_query(F.data == "menu_file")
async def menu_file(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to remove admin privileges from a user here
        await query.answer()
        await query.message.edit_text("Fayllar bilan ishlash bo'limi", reply_markup=FileMenu)
    else:
        await query.answer()
        await query.answer("Siz admin emasiz")

