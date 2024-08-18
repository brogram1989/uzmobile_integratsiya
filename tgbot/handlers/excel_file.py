import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from datetime import date

from loader import bot
from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from tgbot.keyboards.inline import MainMenu
from .admin import is_admin, is_user
from aiogram.fsm.context import FSMContext
from tgbot.states.bot_states import FindId
from tgbot.keyboards.dynamic_inline_keyboardbuilder import InlineKeyboardBuilder


excel_router = Router()

async def download_file(file_id):
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    return BytesIO(downloaded_file.read()), file_info


#integratsiya faylini serverga yuklash handleri
@excel_router.callback_query(F.data == "file_upload")
async def file_upload(query: CallbackQuery, state: FSMContext):
    if is_admin(query.from_user.id):
        # Your logic to remove admin privileges from a user here
        await query.answer()
        await query.answer("📎 tegishli faylni serverga yuklang")
        await query.message.answer(f"📎 faylni serverga yuklang", reply_markup=ReplyKeyboardRemove())
        await state.set_state(FindId.send_ip_file)
    else:
        await query.answer()
        await query.message.answer("🚫Siz admin emassiz, fayl yuklolmaysiz!")


# 3 martta urinishdan so'ng statedan chiqib ketadigan qilish uchun i ni elon qilamiz
soni = 1
xisob = 0

#integratsiya faylini yuklash uchun callback handler
@excel_router.message(FindId.send_ip_file)
async def handle_ip_document(message: Message, state:FSMContext):
    global excel_data, soni, sheet_names  # Declare the global variable
   # sheet_names ni bo'shhatib olamiz xar bir fayl yuklaganda
    sheet_names = []
    try:
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING,
        )
        # Download the Excel file
        file_content, info = await download_file(message.document.file_id)

        # Load the Excel file into a Pandas DataFrame
        excel_data = pd.read_excel(file_content, sheet_name='ZTE_&_HUAWEI', engine='openpyxl')
        # Convert the relevant columns to object type first
        date_columns = ["Доставка на объект", "Монтаж в процессе", "Монтаж заверщен", "Запуск в процессе", "Запуск",
                        "План запуска"]
        for col in date_columns:
            excel_data[col] = excel_data[col].astype('object')
        #excel_data da data typelarni keyinchalik ishlov uchun belgilab olish 5chi qatordan datetypega o'tkazamiz.
        #chunki obektlar 4chi qatordan boshlanyabdi. 3birinchi qatordan boshlanganda
        #endi ba'zi qatorlarni yil, oy, kun formatiga o'tkazib olamiz

        excel_data.loc[3:, "Доставка на объект"] = pd.to_datetime(excel_data.loc[3:, "Доставка на объект"],
                                                                  errors="coerce").dt.date
        excel_data.loc[3:, "Монтаж в процессе"] = pd.to_datetime(excel_data.loc[3:, "Монтаж в процессе"],
                                                                  errors="coerce").dt.date
        excel_data.loc[3:, "Монтаж заверщен"] = pd.to_datetime(excel_data.loc[3:, "Монтаж заверщен"],
                                                                  errors="coerce").dt.date
        excel_data.loc[3:, "Запуск в процессе"] = pd.to_datetime(excel_data.loc[3:, "Запуск в процессе"],
                                                                  errors="coerce").dt.date
        excel_data.loc[3:, "Запуск"] = pd.to_datetime(excel_data.loc[3:, "Запуск"],
                                                                  errors="coerce").dt.date
        excel_data.loc[3:, "План запуска"] = pd.to_datetime(excel_data.loc[3:, "План запуска"],
                                                                  errors="coerce").dt.date


        await message.reply(f"\n \n <b>✅ Excel fayl muvafaqqiyatli yuklandi.</b>")
    except Exception as e:
        await message.reply(f"❌❓Qandaydir xatolik yuzaga keldi! : <b>{str(e)}</b>\n"
                            f"faylni yuklashga qaytadan urinib ko'ring !📎\n"
                            f"{soni}chi urinish. 3chi urinishdan so'ng faylni yuklash xolatdan chiqib ketasiz.\n"
                            f"xolatdan chiqib ketish uchun /reset buyrug'ini yozing")
        if soni == 3:
            await state.clear()
            await message.answer(f"Faylni yuklash xolatidan chiqib kettingiz, to'g'ri faylni yuklayotganingizga ishonchingiz komilmi?")
        else:
            soni += 1
            # Do not finish the state, allowing the user to try again
            return

    #agar tegishli fayl yuklansa statedan chiqib ketamiz
    await state.clear()
#_____________________________________________________________________________________________________________________#
#qidiruv bo'limiga o'tamiz
@excel_router.callback_query(F.data == "qidir")
@excel_router.callback_query(F.data == "again_search")
async def find_bs_command(query: CallbackQuery, state: FSMContext):
    if is_user(query.from_user.id):
        # Your logic to remove admin privileges from a user here
        await query.answer()
        await query.message.answer(f"Qidirmoqchi bo'lganingiz BS id si yoki nomini kirgazing.\n"
                                   f"BS ID <code>REGXXXX</code> yoki <code>BS Name</code>", reply_markup=ReplyKeyboardRemove())
        await state.set_state(FindId.site_id)
    else:
        await query.answer()
        await query.message.answer("🚫Siz foydalanuvchi emassiz!")

#saytni qidiruv uchun berganda ushlab oluvchi handler
@excel_router.message(FindId.site_id)
async def pick_siteid_fromuser(message: Message, state: FSMContext):
    try:
        # Get user information
        find_id = message.text
        xisob = 0
        if excel_data is not None:
            # Perform data operations
            df = excel_data
            df['BTS Name'] = df['BTS Name'].str.upper()
            maska = df['BTS ID'].str.contains(find_id.upper(), na=False) | df['BTS Name'].str.contains(find_id.upper(), na=False)
            search_result = df[maska].sort_values(by=['BTS ID']).head(10)[['BTS ID', 'BTS Name']]
            df['BTS Name'] = df['BTS Name'].str.capitalize()

            if search_result.shape[0] != 0:
                # Handle case when search result is found
                keyboard_builder = InlineKeyboardBuilder()
                for index, row in search_result.iterrows():
                    button_name = row['BTS ID'] + '     ' + row['BTS Name'].title()
                    callback_data = 'btsid' + row['BTS ID']
                    keyboard_builder.add_button(button_name, callback_data)

                keyboard_builder.add_button("🔎boshqa saytlarni qidirib ko'rish", callback_data='again_search')
                site_inlinekeyboard = keyboard_builder.create_keyboard()
                await message.answer("Topilgan obektlar\nKerakli BS ni tanlang!\n", reply_markup=site_inlinekeyboard)
            else:
                # Handle case when search result is empty
                xisob += 1  # Increment xisob
                if xisob >= 3:
                    await message.reply(f"charchatib yubordingiz broo! keyinroq bir urunib ko'ring ! ")
                    await state.clear()
                else:
                    await message.reply(f"Siz kiritayotgan id yoki nomdagi BS ma'lumotlar bazasidan topilmadi, qaytadan urunib ko'ring")

    except Exception as e:
        await message.reply(f" ❌❓Qandaydir xato sodir bo'ldi : <b>{str(e)}</b>\n"
                            f"kerakli fayl yuklanmagan bo'lsa, admin avval faylni yuklashi kerak")
    await state.clear()
#___________________________________________________________________________________________________________#
#user tomonidan tanlangan sayt xaqida ma'lumot chiqazish
@excel_router.callback_query(lambda c: c.data.startswith('btsid'))
async def handle_btsid_button(query: CallbackQuery):
    try:
        # Extract the BTSID from the callback data
        bts_id = query.data[5:]

        # Retrieve the corresponding row from the DataFrame
        selected_row = excel_data[excel_data['BTS ID'] == bts_id].iloc[0]

        # Extract information from the selected row
        bts_name = selected_row['BTS Name']
        # Add more columns as needed
        #bts_address = selected_row['BTS adres']
        bts_status = selected_row['Online\\New sites']
        bts_type = selected_row['Type BTS']
        curent_tec = selected_row['Существующая технология']
        moder_tec = selected_row['Технология после модернизации']
        vendor = selected_row['Vendor']
        phase = selected_row['Contract and PO number']
        supply_eq = selected_row["Доставка на объект"]
        mounting_ongoing = selected_row["Монтаж в процессе"]
        mounting = selected_row["Монтаж заверщен"]
        launch_ongoing = selected_row["Запуск в процессе"]
        launch = selected_row["Запуск"]
        region = selected_row["Region"]
        comment = selected_row["Примечание"]
        # # Location for the 📍 icon
        # long = selected_row['Longitude']
        # lat = selected_row['Latitude']
        # url = f"http://maps.google.com/maps?q={lat},{long}"

        info_about_bs = f"""
Tanlangan BTS bo'yicha ma'lumotlar: \n
1. <b>🆔:</b>  {bts_id}
2. <b>Nomi:</b>  {bts_name}
3. <b>📶online/offline:</b>  {bts_status}
4. <b>Konfiguratsiya raqami:</b>   {bts_type}
5. <b>📂mavjud texnologiya:</b>   {curent_tec}
6. <b>🗂modernizatsiyadan keyingi texnologiya:</b>  {moder_tec}
7. <b>🗺region:</b>   {region}
8. <b>vendor:</b>     {vendor} 
9. <b>faza:</b>   {phase}
10. <b>📆 qurilmalar yetkazildi 🚛:</b>  {supply_eq}
11. <b>📆 obekt montaji boshlandi ⚙️🛠:</b>  {mounting_ongoing}
12. <b>📆 obekt montaji tugallandi ✅🛠:</b>   {mounting}
13. <b>📆 zapusk boshlandi ⚙️📶:</b>   {launch_ongoing}
14. <b>📆 zapusk bo'ldi ✅📶:</b>  {launch}
15. <b> obekt bo'yicha izoh :</b>  {comment}
<a href="http://maps.google.com/maps?q=">📍lokatsiya</a>

  """
        bs_keyboard = InlineKeyboardBuilder()

        for_keyboard = {"🚚qurilma yetkazildi":f"done_supplyeq-{bts_id}",
                        "🅿️🛠montaj boshlandi":f"done_fiteq-{bts_id}",
                        "✅🛠montaj tugallandi":f"done_finishfiteq-{bts_id}",
                        "🅿️⚙️zapusk boshlandi":f"done_startlaunch-{bts_id}",
                        "📋izoh yozish":f"comment-{bts_id}",
                        }
        for button_name , callback_data in for_keyboard.items():
            bs_keyboard.add_button(button_name, callback_data)
        #agar foydalanuvchi admin bo'lsagina zapuskni belgilash xuquqi mavjud bo'ladi
        #oxirida admin faqat zapusk bo'ldini belgilaydigan qilaman, Shuni Sherzod akadan so'rashim kerak
        #oxirida admin faqat zapusk bo'ldini belgilaydigan qilaman, Shuni Sherzod akadan so'rashim kerak
        if is_admin(query.from_user.id):
            bs_keyboard.add_button("✅📶zapusk bo'ldi", f"done_finishlaunch-{bts_id}")
        bs_keyboard.add_button("🏘 bosh menuga qaytish","menu")
        bs_keyboard_done = bs_keyboard.create_keyboard()

        await bot.answer_callback_query(query.id,
                                    f"{query.from_user.first_name}, siz : {bts_id} - {bts_name} ni tanladingiz")
        await query.message.answer(f"{info_about_bs} \n", reply_markup=bs_keyboard_done)
    except IndexError:
        # Handle the case where the selected BTSID is not found in the DataFrame
        await bot.answer_callback_query(query.id, "Xatolik! Qidirilayotgan BS topilmadi")

#______________________________________________________________________________________________________________#
#regionlar tanlanganda uzel agrigatsiyalarni ko'rsatuvchi tugma
@excel_router.callback_query(lambda callback_query: callback_query.data.startswith('done_'))
async def handle_user_choice(query: CallbackQuery):
    try:
        user_choice = query.data[len('done_'):]  # Extract theuser choice from the callback data
        command, bts_id = user_choice.split('-')

        today_date = date.today()
        if command == 'supplyeq':
            excel_data.loc[excel_data["BTS ID"] == bts_id, "Доставка на объект"] = today_date
            await query.answer()
            await query.message.answer(f"{bts_id} obektiga {today_date} sanasida qurilma yetkazildi")
        elif command == "fiteq":
            excel_data.loc[excel_data["BTS ID"] == bts_id, "Монтаж в процессе"] = today_date
            await query.answer()
            await query.message.answer(f"{bts_id} obektida {today_date} sanada montaj ishlari boshlandi")
        elif command == "finishfiteq":
            excel_data.loc[excel_data["BTS ID"] == bts_id, "Монтаж заверщен"] = today_date
            await query.answer()
            await query.message.answer(f"{bts_id} obektida {today_date} sanada montaj ishlari tugallandi")
        elif command == "startlaunch":
            excel_data.loc[excel_data["BTS ID"] == bts_id, "Запуск в процессе"] = today_date
            await query.answer()
            await query.message.answer(f"{bts_id} obektida {today_date} sanada zapusk boshlandi")
        elif command == "finishlaunch":
            excel_data.loc[excel_data["BTS ID"] == bts_id, "Запуск"] = today_date
            await query.answer()
            await query.message.answer(f"{bts_id} obektida {today_date} sanada zapusk bo'ldi ✅✅✅")

    except Exception as e:
        await query.answer()
        await query.message.answer(f"❌❓qandaydir xatolik yuzaga keldi ! : <b>{str(e)}</b>\n")

@excel_router.callback_query(lambda callback_query: callback_query.data.startswith('comment'))
async def handle_comment(query: CallbackQuery, state: FSMContext):
    try:
        if is_user(query.from_user.id):
            comment, bts_id = query.data.split('-')
            await query.answer()
            await query.message.answer(f"📎{query.from_user.first_name} {bts_id} ob'ekti bo'yicha izohingizni yozing", reply_markup=None)
            await state.update_data(bts_id=bts_id)  # Store bts_id in state
            await state.set_state(FindId.comment)
        else:
            await query.message.answer("🚫Siz user emassiz, fayl yuklolmaysiz!")
    except Exception as e:
        await query.answer()
        await query.message.answer(f"❌❓qandaydir xatolik yuzaga keldi ! : <b>{str(e)}</b>\n")


#bts uchun komment yozishga handler
@excel_router.message(FindId.comment)
async def user_comment_handle(message: Message, state:FSMContext):
    try:
        comment = message.text
        data = await state.get_data()  # Retrieve the stored data
        bts_id = data.get('bts_id')
        excel_data.loc[excel_data["BTS ID"] == bts_id, "Примечание"] = comment
        await message.answer(f"{message.from_user.first_name} sizning izohingiz {bts_id} uchun saqlandi")
        await state.clear()
    except Exception as e:
        await message.answer()
        await message.answer(f"❌❓qandaydir xatolik yuzaga keldi ! : <b>{str(e)}</b>\n")

#_____________________________________________________________________________________________________#
#statistika bo'limi uchun handlerlar qismi
#bugungi reja uchun funksiya

@excel_router.callback_query(lambda callback_query: callback_query.data.startswith('todays_plan'))
async def todays_launch_plan(query: CallbackQuery):
    try:
        today_date = date.today()


        # Filter the DataFrame for rows where the "Запуск в процессе" column equals today_date
        filtered_rows = excel_data[(excel_data["Запуск в процессе"] == today_date) &
                                   (excel_data['Запуск'].isna() | (excel_data['Запуск'] == ''))]

        # Initialize variables
        spiska_zapusk = ''
        spiska_modern = ''
        i = 0
        j = 0
        #

        # # Check if there are any rows matching today's date
        if not filtered_rows.empty:
            for index, row in filtered_rows.iterrows():
                bts_name = row["BTS Name"].title()
                bts_old_texnologiya = row["Существующая технология"]
                bts_texnologiya = row["Технология после модернизации"]
                today = row["Запуск в процессе"]

                if row["Online\\New sites"] in ["New Site", "New site", "new site", "NEW SITE"]:
                    bts_id_zapusk = row["BTS ID"]
                    i += 1
                    spiska_zapusk += f"<b>{i}. {bts_id_zapusk} {bts_name}</b>  {bts_texnologiya}\n\n"
                elif row["Online\\New sites"] in ["Online", "online", "ONLINE"]:
                    bts_id_modern = row["BTS ID"]
                    j += 1
                    spiska_modern += f"<b>{j}. {bts_id_modern} {bts_name}</b> {bts_old_texnologiya} ⏩🆕 {bts_texnologiya}\n\n"

            if i != 0:
                await query.answer()
                await query.message.answer(
                    f"Bugun, {str(today_date)} kuni yangi ishga tushirilishi rejalashtirilgan BS(lar) soni {i} ta\n"
                    f"{spiska_zapusk}\n", reply_markup=None)
            if i == 0:
                await query.answer()
                await query.message.answer(
                    f"Bugun, {str(today_date)} kuni yangi ishga tushirilishi rejalashtirilgan BS(lar) yo'q\n",
                    reply_markup=None)

            if j != 0:
                await query.answer()
                await query.message.answer(
                    f"Bugun, {str(today_date)} kuni {j} ta BS(lar)da SWAP va modernizatsiya ishlari rejalashtirilgan\n"
                    f"{spiska_modern}\n", reply_markup=None)

            if j == 0:
                await query.answer()
                await query.message.answer(
                    f"Bugun, {str(today_date)} kuni modernizatsiya uchun rejalashtirilgan BS(lar) yo'q\n", reply_markup=None)

        else:
            await query.answer()
            await query.message.answer(f"Bugun ishga tushirilishi rejalashtirilgan sayt topilmadi. ")

    except Exception as e:
        print(e)
        await query.answer()
        await query.message.answer(f"Noma'lum xatolik yuzaga keldi! <code>{e}</code>")


#_____________________________________________________________________________________________________________________#

#⚙️jarayonda uchun qism

@excel_router.callback_query(lambda callback_query: callback_query.data.startswith('on_going'))
async def in_progress(query: CallbackQuery):
    try:
        today_date = date.today()
        # Check if there are any rows matching today's date
        if not excel_data.empty:
            # If there are matching rows, send them as a message
            i = 0
            j = 0
            x = 0
            dostavka_vobekt = ''
            montaj_nachat = ''
            ne_zapushen = ''
            excel_data["BTS Name"] = excel_data["BTS Name"].astype(str)

            for index, row in excel_data.iterrows():
                bts_id = row["BTS ID"]
                bts_name = row["BTS Name"].title()
                # Check if the row["Монтаж заверщен"] value is not NaT and row["Запуск"] value is not Na
                if pd.notna(row["Монтаж заверщен"]) and pd.isna(row["Запуск"]):
                    # Define Монтаж заверщен date
                    sites_date = row["Монтаж заверщен"]

                    # Calculate the difference in days
                    day_difference = (today_date - sites_date).days
                    x += 1
                    ne_zapushen += f"<b>{x}. {bts_id} </b> {bts_name}  {day_difference} kundan beri.\n"
                    #ne_zapushen = ne_zapushen.join(f"<b>{x}. {bts_id} </b> {bts_name}  {day_difference} kundan beri.\n")
            await query.answer()
            await query.message.answer(f"<b>quyidagi {x} ta obektlarda montaj ishlari yakunlangan, lekin ishga tushmagan:</b>\n"
                                 f"{ne_zapushen}\n",
                                 reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Ishga tushish jarayonda turgan obektlar mavjud emas!")

    except Exception as e:
        print(e)
        await query.answer()
        await query.message.answer(f"Noma'lum xatolik yuzaga keldi! <code>{e}</code>")


#___________________________________________________________________________________________#

#_____________________________________________________________________________________________________________________#


#⚙️bugungi bajarilgan ishlar uchun qism
@excel_router.callback_query(lambda callback_query: callback_query.data.startswith('todays_action'))
async def todays_done(query: CallbackQuery):
    try:
        today_date = date.today()
        excel_data["BTS Name"] = excel_data["BTS Name"].astype(str)

        # If there are matching rows, send them as a message
        y = 0
        m = 0
        i = 0
        j = 0
        x = 0

        #xar bir qism uchun df ni alohida-alohida filtrlab olamiz, umumiy filtrlaganimda ishlamadi

        zapusk_today = ''
        modern_today = ''
        filtred_zapusk = excel_data[(excel_data["Запуск"] == today_date)]
        for index, row in filtred_zapusk.iterrows():
            bts_id = row["BTS ID"]
            bts_name = row["BTS Name"].title()
            bts_old_texnologiya = row["Существующая технология"]
            bts_texnologiya = row["Технология после модернизации"]
            bts_sts = row["Online\\New sites"]
            if row["Online\\New sites"] in ["New Site", "New site", "new site", "NEW SITE"]:
                y += 1
                zapusk_today += f"<b>{y}. {bts_id} {bts_name}</b>  {bts_texnologiya}\n"
            elif row["Online\\New sites"] in ["Online", "online", "ONLINE"]:
                bts_id_modern = row["BTS ID"]
                m += 1
                modern_today += f"<b>{m}. {bts_id_modern} {bts_name}</b> {bts_old_texnologiya} ⏩🆕 {bts_texnologiya}\n"

        montaj_zavershyon = ''
        filtred_montaj_zavershyon = excel_data[(excel_data["Монтаж заверщен"] == today_date)]
        for index, row in filtred_montaj_zavershyon.iterrows():
            bts_id = row["BTS ID"]
            bts_name = row["BTS Name"].title()
            bts_old_texnologiya = row["Существующая технология"]
            bts_texnologiya = row["Технология после модернизации"]
            x += 1
            montaj_zavershyon += f"<b>{x}. {bts_id}  {bts_name} </b> {bts_old_texnologiya} ⏩🆕  {bts_texnologiya}\n"

        montaj_nachat = ''
        filtred_montaj_nachat = excel_data[(excel_data["Монтаж в процессе"] == today_date)]
        for index, row in filtred_montaj_nachat.iterrows():
            bts_id = row["BTS ID"]
            bts_name = row["BTS Name"].title()
            bts_old_texnologiya = row["Существующая технология"]
            bts_texnologiya = row["Технология после модернизации"]
            j += 1
            montaj_nachat += f"<b>{j}. {bts_id}  {bts_name} </b> {bts_old_texnologiya} ⏩🆕  {bts_texnologiya}\n"

        dostavka_vobekt = ''
        filtred_dostavka_vobekt = excel_data[(excel_data["Доставка на объект"] == today_date)]
        for index, row in filtred_dostavka_vobekt.iterrows():
            bts_id = row["BTS ID"]
            bts_name = row["BTS Name"].title()
            bts_old_texnologiya = row["Существующая технология"]
            bts_texnologiya = row["Технология после модернизации"]
            i += 1
            dostavka_vobekt += f"<b>{i}. {bts_id}  {bts_name} </b>  {bts_old_texnologiya} ⏩🆕  {bts_texnologiya}\n"
        #foydalanuvchiga yuboramiz
        if dostavka_vobekt:
            await query.answer()
            await query.message.answer(f"<b>Bugun {today_date} sanasida quyidagi {i} ta obektga qurilmalar yetkazildi:</b>\n"
                                 f"{dostavka_vobekt}\n", reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Bugun {today_date} sanasida obektlarga qurilmalar yetkazilmadi.")

        if montaj_nachat:
            await query.answer()
            await query.message.answer(f"<b>Bugun {today_date} sanasida quyidagi {j} ta obektta montaj ishlari boshlandi:</b>\n"
                                 f"{montaj_nachat}\n", reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Bugun {today_date} sanasida obektlarda montaj ishlari boshlanmadi.")

        if montaj_zavershyon:
            await query.answer()
            await query.message.answer(f"<b>Bugun {today_date} sanasida  quyidagi {x} ta obektta montaj ishlari tugallandi:</b>\n"
                                 f"{montaj_zavershyon}\n", reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Bugun {today_date} sanasida obektlarda montaj tugallanmadi.")

        if zapusk_today:
            await query.answer()
            await query.message.answer(f"<b>Bugun {today_date} sanasida quyidagi {y} ta obekt ishga tushdi:</b>\n"
                                 f"{zapusk_today}\n", reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Bugun {today_date} sanasida zapusk bo'lmadi.")
        if modern_today:
            await query.answer()
            await query.message.answer(f"<b>Bugun {today_date} sanasida quyidagi {m} ta obekt modernizatsiya bo'ldi:</b>\n"
                                 f"{modern_today}\n", reply_markup=None)
        else:
            await query.answer()
            await query.message.answer(f"Bugun {today_date} sanasida modernizatsiya ishlari bo'lmadi.")

    except Exception as e:

        print(f"An error occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Traceback: {e.__traceback__}")
        await query.answer()
        await query.message.answer(f"Noma'lum xatolik yuzaga keldi! <code>{e}</code>")
#____________________________________________________________________________________________________#
# #endi grafigini va umumiy statiskani chiqazish uchun handler qilamiz

@excel_router.callback_query(lambda c: c.data == "total_graphic_statistics")
async def total_statistics(query: CallbackQuery):
    try:
        if is_user(query.from_user.id):
            today_date = date.today()
            # Group the data by Region and Online\New sites, and count the launched base stations
            grouped_data = excel_data.groupby(['Region', r'Online\New sites'])['Запуск'].count().unstack()

            # Calculate the total number of base stations for each region
            total_stations = excel_data.groupby('Region').size()

            # Calculate the number of launched stations
            launched_stations = grouped_data.sum(axis=1)

            # Calculate the percentage of launched stations
            percentage_launched = (launched_stations / total_stations) * 100

            # Function to create the percentage chart
            def create_percentage_chart():
                fig, ax = plt.subplots(figsize=(14, 8))
                bars = percentage_launched.plot(kind='bar', ax=ax)
                ax.set_title(f"{today_date} sanasi bo'yicha viloyatlar kesimida ishga tushgan BS larning foiz ulushi", fontsize=16)
                ax.set_xlabel('Viloyatlar', fontsize=12)
                ax.set_ylabel('Ishga tushgan BS lar foizi', fontsize=12)
                ax.set_ylim(0, 100)

                # Add percentage labels on the bars
                for i, bar in enumerate(bars.patches):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height / 2,
                            f'{percentage_launched[i]:.1f}%',
                            ha='center', va='center', fontsize=10, color='white')

                # Add launched BS numbers above each bar
                for i, launched in enumerate(launched_stations):
                    ax.text(i, percentage_launched[i], f'{launched}', ha='center', va='bottom')

                plt.tight_layout()

                # Save the plot to a BytesIO object
                img_buffer = BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close()

                return img_buffer

            # Create the percentage chart
            chart_buffer_procent = create_percentage_chart()

            # Send the chart as a photo
            await query.message.answer_photo(
                BufferedInputFile(chart_buffer_procent.getvalue(), filename="percentage_chart.png"),
                caption=f"{today_date} sanasi bo'yicha viloyatlar kesimida ishga tushgan tayanch stansiyalari foizi"
            )

            # Function to create and save the first chart
            def create_quantity_chart():
                fig, ax = plt.subplots(figsize=(14, 8))
                grouped_data.plot(kind='bar', stacked=True, ax=ax)
                ax.set_title(f"{today_date} sanasi bo'yicha viloyatlar kesimida ishga tushgan va modernizatsiya bo'lgan BS lar", fontsize=16)
                ax.set_xlabel('Viloyat', fontsize=12)
                ax.set_ylabel('Ishga tushgan BS lar soni', fontsize=12)
                ax.legend(title='Online\\New sites', bbox_to_anchor=(1.05, 1), loc='upper left')

                # Add quantity labels on the bars
                for c in ax.containers:
                    ax.bar_label(c, label_type='center')

                # Add total launched numbers above each bar
                for i, total in enumerate(launched_stations):
                    ax.text(i, total, f'Umumiy: {total}', ha='center', va='bottom')

                plt.tight_layout()

                # Save the plot to a BytesIO object
                img_buffer = BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                plt.close()

                return img_buffer

            # Create the percentage chart
            chart_buffer_quantity = create_quantity_chart()

            # Send the chart as a photo
            await query.message.answer_photo(
                BufferedInputFile(chart_buffer_quantity.getvalue(), filename="percentage_chart.png"),
                caption=f"{today_date} sanasi bo'yicha viloyatlar kesimida ishga tushgan tayanch stansiyalari soni"
            )

            # Generate and send detailed statistics as text
            stats_text = f"{today_date} sanasi bo'yicha viloyatlar kesimida ishga tushgan BS lar xaqida umumiy ma'lumot:\n\n"
            for region in total_stations.index:
                total = total_stations[region]
                launched = launched_stations[region]
                percentage = percentage_launched[region]
                stats_text += f"<b>{region}</b>:\n"
                stats_text += f"  Total BS: <b>{total}</b>\n"
                stats_text += f"  Launched BS: <b>{launched}</b>\n"
                stats_text += f"  Percentage Launched: <b>{percentage:.2f}%</b>\n"
                stats_text += "  Breakdown:\n"
                for category in grouped_data.columns:
                    count = grouped_data.loc[region, category]
                    stats_text += f"    - {category}: <b>{count}</b>\n"
                stats_text += "\n"

            await query.message.answer(stats_text)

        else:
            await query.answer()
            await query.message.answer("🚫Siz foydalanuvchi emassiz", reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        print(f"An error occurred: {e}")
        await query.message.answer(f"Qandaydir xatolik sodir bo'ldi! {e}")

#____________________________________________________________________________________________________#

#ozgartirilgan excel_data dict ni yangi excel fayl yaratib , foydalanuvchiga yuborish hendleri
@excel_router.callback_query(lambda c: c.data == "file_download")
async def download_ip_file(query: CallbackQuery):
    try:
        if is_admin(query.from_user.id):
            today_date = date.today()
            await query.answer()
            await query.answer("📎📊📈 Faylni serverdan qabul qilib oling\n yuklanmoqda...", reply_markup=ReplyKeyboardRemove())

            file_path = Path(f'integratsiya_fayli_{today_date}.xlsx')

            # Write the DataFrame to the Excel file
            excel_data.to_excel(file_path, index=False, sheet_name='ZTE_&_HUAWEI')

            # Check if the file was processed successfully
            if file_path.exists():
                # Send the processed file to the user
                await query.bot.send_chat_action(chat_id=query.message.chat.id, action=ChatAction.UPLOAD_DOCUMENT)
                await query.bot.send_document(query.from_user.id, BufferedInputFile.from_file(file_path))
                file_path.unlink()
            else:
                await query.answer()
                await query.message.reply("❌ Faylni yozishda xatolik yuz berdi")
        else:
            await query.answer()
            await query.answer("🚫Siz admin emassiz, fayl yuklolmaysiz!", reply_markup=ReplyKeyboardRemove())
            await query.message.answer("🚫Siz admin emassiz, fayl yuklolmaysiz!", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        await query.message.reply(f"❌❓Возникло ошибка ! : <b>{str(e)}</b>\n")
    finally:
        # Always remove the file after the operation
        if file_path.exists():
            file_path.unlink()
            await query.answer()
            await query.message.answer("Temporary file deleted.", reply_markup=ReplyKeyboardRemove())
