from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


MainMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔎qidirish", callback_data='qidir'),
        ],
        [
            InlineKeyboardButton(text='📊statistika', callback_data='statistika'),
        ],
        [
            InlineKeyboardButton(text='💻admin buyruqlari', callback_data='admin_commands'),
        ],
    ],
)
#______________________________________________________________________________________________#
#admin buyruqlari uchun keyboardlarni ishlab chiqamiz

AdminMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💾fayllar bilan ishlash", callback_data='menu_file'),
        ],
        [
            InlineKeyboardButton(text='👨🏻‍💻foydalanuvchilar bilan ishlash', callback_data='menu_users'),
        ],
        [
            InlineKeyboardButton(text="🏘 bosh menuga qaytish", callback_data='menu'),
        ],
    ],
)
#fayllarni yuklash uchun keyboard
FileMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="💾⬆️ ishchi faylni serverga yuklash", callback_data="file_upload"),
        ],
        [
            InlineKeyboardButton(text="💾⬇️ ishchi faylni serverdan yuklash", callback_data="file_download"),
        ],
        [
            InlineKeyboardButton(text="🔙 ortga qaytish", callback_data='admin_commands'),
            InlineKeyboardButton(text="🏘bosh menuga qaytish", callback_data='menu'),
        ],
    ],
)


#foydalanuvchilarni qo'shish o'chirish buyrug'i

user_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="➕👤 foydalanuvchi qo'shish", callback_data='add_user'),
        ],
        [
            InlineKeyboardButton(text="❌👤 foydalanuvchini o'chirish", callback_data='del_user'),
        ],
        [
            InlineKeyboardButton(text="✅🥷 foydalanuvchini admin qilish", callback_data='set_admin'),
        ],
        [
            InlineKeyboardButton(text="❌🥷 adminlar ro'yxatidan chiqazish", callback_data='del_admin'),
        ],
        [
            InlineKeyboardButton(text="👥📝 foydalanuvchilar ro'yxati", callback_data='list_users'),
        ],
        [
            InlineKeyboardButton(text="🔙 ortga qaytish", callback_data='admin_commands'),
            InlineKeyboardButton(text="🏘bosh menuga qaytish", callback_data='menu'),
        ],
    ],
)
#____________________________________________________________________________________________________________#
MenuStat = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⚙️️jarayonda", callback_data='on_going'),
        ],
        [
            InlineKeyboardButton(text='⚙️bugungi bajarilgan ishlar', callback_data='todays_action'),
        ],
        [
            InlineKeyboardButton(text='📆bugungi ishga tushish rejasi', callback_data='todays_plan'),
        ],
        [
            InlineKeyboardButton(text="📉📈📊 umumiy grafik ma'lumot", callback_data='total_graphic_statistics'),
        ],
        [
            InlineKeyboardButton(text="🏘bosh menuga qaytish", callback_data='menu'),
        ],
    ],
)