import os
import logging
from aiogram import Bot
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher, FSMContext
from captcha.image import ImageCaptcha
import random
from random import randrange
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

from telegram_bot.message_s import MESSAGES
from telegram_bot.KeyboardButton import BUTTON_TYPES
from telegram_bot.utils import StatesUsers
from cfg.database import Database


db = Database('cfg/database')


async def start_bot(dp):
    event_loop.create_task(dp.start_polling())


def bot_init(event_loop, token):
    bot = Bot(token)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()

    # ===================================================
    # =============== ПОЛУЧЕНИЕ КУРСА BTC ===============
    # ===================================================
    def convert_rub_to_btc(amount, coin):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": f"{coin}",
                "vs_currencies": "rub"
            }

            response = requests.get(url, params=params).json()[coin]["rub"]
            print(response)
            amount_btc = amount / response
            print(amount_btc)
            return amount_btc

        except Exception as ex:
            print(ex)
            return "Не удалось получить курс обмена"

    # ===================================================
    # ================== СОЗДАНИЕ КАПЧИ =================
    # ===================================================
    async def generation_captha(message):
        image = ImageCaptcha(width=250, height=100)

        random_numbers = []
        for _ in range(5):
            random_number = random.randint(0, 9)
            random_numbers.append(str(random_number))
        captcha_text = ''.join(random_numbers)

        image.write(captcha_text, f'img/{message.from_user.id}.png')
        with open(f'img/{message.from_user.id}.png', 'rb') as photo:
            await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=MESSAGES["captha"])
        return captcha_text

    # ===================================================
    # ================ СОЗДАНИЕ КЛАВИАТУРЫ ==============
    # ===================================================
    def generation_keyboard():
        keyboard = InlineKeyboardMarkup()

        all_key = db.get_keyboard()

        for i in range(0, len(all_key), 2):
            if i + 1 < len(all_key):
                btn_city_1 = InlineKeyboardButton(text=f"{all_key[i][0]}", callback_data=f"{all_key[i][0]}")
                btn_city_2 = InlineKeyboardButton(text=f"{all_key[i + 1][0]}", callback_data=f"{all_key[i + 1][0]}")
                keyboard.add(btn_city_1, btn_city_2)
            else:
                btn_city = InlineKeyboardButton(text=f"{all_key[i][0]}", callback_data=f"{all_key[i][0]}")
                keyboard.add(btn_city)

        btn_balance = InlineKeyboardButton(text="Баланс (0 руб)", callback_data="balance")
        btn_my_bot = InlineKeyboardButton(text="Мои боты", callback_data="my_bot")
        btn_ref = InlineKeyboardButton(text="Реферальная программа", callback_data="ref")
        btn_last_order = InlineKeyboardButton(text="Последний заказ", callback_data="last_order")
        btn_operator = InlineKeyboardButton(text="Оператор", url="https://t.me/bsk_alicesho0pp")
        btn_support = InlineKeyboardButton(text="Тех.поддержка", url="https://t.me/bsk_allicesup")
        btn_wrk = InlineKeyboardButton(text="Работа", url="https://t.me/Dengi_delay")
        return keyboard.add(btn_balance).add(btn_my_bot).add(btn_ref).add(btn_last_order).add(btn_operator).add(
            btn_support).add(btn_wrk)

    # ============ СОЗДАНИЕ КЛАВИАТУРЫ РАЙОНА ===========
    def generation_keyboard_district(city_name):
        keyboard = InlineKeyboardMarkup()
        try:
            all_key = db.get_keyboard_district(city_name)[0].split("|")

            for key_city in all_key:
                if key_city:
                    btn_city = InlineKeyboardButton(text=f"{key_city}", callback_data=f"{key_city}")
                    keyboard.add(btn_city)
        except:
            ...
        return keyboard.add(InlineKeyboardButton(text="Главное меню", callback_data="menu_home"))

    # ============ СОЗДАНИЕ КЛАВИАТУРЫ ПРОДУКТОВ ==========
    def generation_keyboard_products(city_name, district_name):
        keyboard = InlineKeyboardMarkup()

        try:
            all_key = db.get_keyboard_products(city_name)[0].split("|")
            for key_city in all_key:
                if key_city:
                    if district_name in key_city:
                        new_key = key_city.replace(f"({district_name})", "")
                        btn_city = InlineKeyboardButton(text=f"{new_key}", callback_data=f"{new_key}")
                        keyboard.add(btn_city)
        except:
            ...
        return keyboard.add(InlineKeyboardButton(text="Главное меню", callback_data="menu_home"))

    # ===================================================
    # ================== СТАРТ КОМАНДА ==================
    # ===================================================
    async def start_command(message: Message):
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id, message.from_user.username)
            captcha_text = await generation_captha(message)
            state = dp.current_state(user=message.from_user.id)
            await state.update_data(captha=captcha_text)
            await state.set_state(StatesUsers.all()[2])

        else:
            await bot.send_message(text=MESSAGES["start_user"], chat_id=message.from_user.id,
                                   reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
            await bot.send_message(text=MESSAGES["start_user_2"], chat_id=message.from_user.id,
                                   reply_markup=generation_keyboard())

            state = dp.current_state(user=message.from_user.id)
            await state.finish()

    async def start_command_inline(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["start_user_2"], reply_markup=generation_keyboard())
        state = dp.current_state(user=callback.from_user.id)
        await state.finish()

    # ================== ПРОХОЖДЕНИЕ КАПЧИ ==================
    async def captha_start(message: Message, state: FSMContext):
        data = await state.get_data()
        if message.text == data["captha"]:
            await bot.send_message(text=MESSAGES["start_user"], chat_id=message.from_user.id,
                                   reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
            await bot.send_message(text=MESSAGES["start_user_2"], chat_id=message.from_user.id,
                                   reply_markup=generation_keyboard())
            await state.finish()
        else:
            captcha_text = await generation_captha(message)

            await state.update_data(captha=captcha_text)
            await state.set_state(StatesUsers.all()[2])

    # ===================================================
    # ================== РЕФЕРАЛЬНАЯ П ==================
    # ===================================================
    async def ref_program(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["ref"], reply_markup=BUTTON_TYPES["BTN_ADD_BOT"])
        await callback.answer()

    # ================== НЕТ ПОКУПОК ==================
    async def not_buy(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["add_bot"], reply_markup=BUTTON_TYPES["BTN_MENU"])
        await callback.answer()

    # =====================================================
    # ================== ПОСЛЕДНИЙ ЗАКАЗ ==================
    # =====================================================
    async def last_order(callback: CallbackQuery):
        await callback.answer(text=MESSAGES["not_order"], show_alert=True)
        await callback.answer()

    # ===================================================
    # ===================== МОИ БОТЫ ====================
    # ===================================================
    async def my_bot(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["my_bot"], reply_markup=BUTTON_TYPES["BTN_ADD_BOT"])
        await callback.answer()

    # ===================================================
    # ================ ПОПОЛНЕНИЕ БАЛАНСА ===============
    # ===================================================
    async def add_balance(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["add_balance"], reply_markup=BUTTON_TYPES["BTN_MENU"])
        await callback.answer()

        state = dp.current_state(user=callback.from_user.id)
        await state.set_state(StatesUsers.all()[0])

    # ================ ВВОД БАЛАНСА ===============
    async def input_balance(message: Message, state: FSMContext):
        if message.text.isnumeric():
            MIN_BALANCE = db.get_all_info("MIN_BALANCE")[0]
            if int(message.text) > MIN_BALANCE:
                await bot.send_message(text=MESSAGES["what_pay"], reply_markup=BUTTON_TYPES["BTN_PAY"],
                                       chat_id=message.from_user.id)
                percent = db.get_all_info("COMMISSION")[0]
                pay_sum = int(message.text) + (int(message.text) * percent / 100)
                await state.update_data(input_pay=int(pay_sum))
                await state.set_state(StatesUsers().all()[1])

            else:
                await bot.send_message(text=f"Минимальное пополнение от {MIN_BALANCE}\nПопробуй ввести снова:",
                                       reply_markup=BUTTON_TYPES["BTN_MENU"], chat_id=message.from_user.id)
                await state.set_state(StatesUsers().all()[0])

        else:
            await bot.send_message(text=MESSAGES["not_balance"], reply_markup=BUTTON_TYPES["BTN_MENU"],
                                   chat_id=message.from_user.id)
            await state.set_state(StatesUsers().all()[0])

    # ================ ОПЛАТА ПО КАРТЕ ===============
    async def pay_card(callback: CallbackQuery, state: FSMContext):
        NUMBER_CARD = db.get_all_info("NUMBER_CARD")[0].split("|")
        data = await state.get_data()
        number_order = random.randint(10000000, 99999999)
        await callback.message.edit_text(text=MESSAGES["pay_card_1"] % number_order, parse_mode="HTML")
        await bot.send_message(
            text=MESSAGES["pay_card_2"] % (number_order, data["input_pay"], NUMBER_CARD[randrange(len(NUMBER_CARD))]),
            reply_markup=BUTTON_TYPES["BTN_MENU_HOME"], chat_id=callback.from_user.id, parse_mode="HTML")
        await bot.send_message(text=MESSAGES["pay_card_3"], reply_markup=BUTTON_TYPES["BTN_PROBLEMS"],
                               chat_id=callback.from_user.id)
        await callback.answer()
        await state.finish()

        await asyncio.sleep(1800)
        await bot.send_message(text=MESSAGES["pay_cancel"] % number_order, chat_id=callback.from_user.id,
                               parse_mode="HTML")

    # ================ ОПЛАТА НА BITCOIN ===============
    async def pay_bitcoin(callback: CallbackQuery, state: FSMContext):
        NUMBER_BITCOIN = db.get_all_info("NUMBER_BTC")[0].split("|")
        data = await state.get_data()
        number_order = random.randint(10000000, 99999999)
        rub_btc = convert_rub_to_btc(int(data["input_pay"]), "bitcoin")
        print(rub_btc)
        num_btc = NUMBER_BITCOIN[randrange(len(NUMBER_BITCOIN))]
        await callback.message.edit_text(
            text=MESSAGES["pay_bitcoin"] % (f"{rub_btc:.8f}", "BTC", num_btc, number_order), parse_mode="HTML")
        with open(f'img/{num_btc}.jpg', 'rb') as photo:
            await bot.send_photo(photo=photo, chat_id=callback.from_user.id, reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
        await bot.send_message(text=MESSAGES["pay_card_3"], reply_markup=BUTTON_TYPES["BTN_PROBLEMS"],
                               chat_id=callback.from_user.id)

        await callback.answer()
        await state.finish()

        await asyncio.sleep(1800)
        await bot.send_message(text=MESSAGES["pay_cancel"] % number_order, chat_id=callback.from_user.id,
                               parse_mode="HTML")

    # ================ ОПЛАТА НА LTC ===============
    async def pay_ltc(callback: CallbackQuery, state: FSMContext):
        NUMBER_BITCOIN = db.get_all_info("NUMBER_LTC")[0].split("|")
        data = await state.get_data()
        number_order = random.randint(10000000, 99999999)
        rub_btc = convert_rub_to_btc(int(data["input_pay"]), "litecoin")
        num_btc = NUMBER_BITCOIN[randrange(len(NUMBER_BITCOIN))]
        await callback.message.edit_text(
            text=MESSAGES["pay_bitcoin"] % (f"{rub_btc:.8f}", "LTC", num_btc, number_order), parse_mode="HTML")
        with open(f'img/{num_btc}.jpg', 'rb') as photo:
            await bot.send_photo(photo=photo, chat_id=callback.from_user.id, reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
        await bot.send_message(text=MESSAGES["pay_card_3"], reply_markup=BUTTON_TYPES["BTN_PROBLEMS"],
                               chat_id=callback.from_user.id)

        await callback.answer()
        await state.finish()

        await asyncio.sleep(1800)
        await bot.send_message(text=MESSAGES["pay_cancel"] % number_order, chat_id=callback.from_user.id,
                               parse_mode="HTML")

    # ===================================================
    # ======================= ГОРОДА ====================
    # ===================================================

    # ==================== ВЫБОР РАЙОНА =================
    async def district(callback: CallbackQuery):
        await callback.message.edit_text(text=MESSAGES["what_district"],
                                         reply_markup=generation_keyboard_district(callback.data))

        state = dp.current_state(user=callback.from_user.id)
        await state.update_data(city=callback.data)
        await state.set_state(StatesUsers.all()[4])

    # ==================== ВЫБОР ПРОДУКТА =================
    async def products(callback: CallbackQuery, state: FSMContext):
        await state.update_data(district=callback.data)
        data = await state.get_data()
        await callback.message.edit_text(text=MESSAGES["what_products"],
                                         reply_markup=generation_keyboard_products(data["city"], callback.data))
        await state.set_state(StatesUsers.all()[5])

    # ================== КАРТОЧКА ВЫБРАННОГО =============
    async def card_selected(callback: CallbackQuery, state: FSMContext):
        await state.update_data(product=callback.data)
        data = await state.get_data()
        number_order = random.randint(10000000, 99999999)
        await state.update_data(number_order=number_order)

        await callback.message.edit_text(
            text=MESSAGES["card_selected"] % (number_order, data["city"], data["district"], callback.data),
            reply_markup=BUTTON_TYPES["BTN_WHAT_PAY"], parse_mode="HTML")
        await state.set_state(StatesUsers.all()[6])

    # ================== БАЛАНС ПОЛЬЗОВАТЕЛЯ =============
    async def balance_user(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(text=MESSAGES["balance_user"], reply_markup=BUTTON_TYPES["BTN_PAY"])
        await state.set_state(StatesUsers.all()[7])

    # ================== ОПЛАТА КАРТА/БИТКОИН =============
    async def buy_product(callback: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        matches = re.findall(r'\((.*?)руб\)', data["product"])[-1]
        percent = db.get_all_info("COMMISSION")[0]
        matches = int(int(matches) + (int(matches) * percent / 100))
        NUMBER_BITCOIN = db.get_all_info("NUMBER_BTC")[0].split("|")
        NUMBER_LTC = db.get_all_info("NUMBER_LTC")[0].split("|")
        NUMBER_CARD = db.get_all_info("NUMBER_CARD")[0].split("|")
        if callback.data == "bitcoin" or callback.data == "ltc":
            try:
                if callback.data == "bitcoin":
                    num_btc = NUMBER_BITCOIN[randrange(len(NUMBER_BITCOIN))]
                    rub_btc = convert_rub_to_btc(int(matches), "bitcoin")
                    wallets = "BTC"
                else:
                    num_btc = NUMBER_LTC[randrange(len(NUMBER_LTC))]
                    rub_btc = convert_rub_to_btc(int(matches), "litecoin")
                    wallets = "LTC"

                await callback.message.edit_text(
                    text=MESSAGES["pay_bitcoin"] % (f"{rub_btc:.8f}", wallets, num_btc, data["number_order"]),
                    parse_mode="HTML")
                with open(f'img/{num_btc}.jpg', 'rb') as photo:
                    await bot.send_photo(photo=photo, chat_id=callback.from_user.id,
                                         reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
                await bot.send_message(text=MESSAGES["pay_card_3"], reply_markup=BUTTON_TYPES["BTN_PROBLEMS"],
                                       chat_id=callback.from_user.id)

                await callback.answer()
                await state.finish()

                await asyncio.sleep(1800)
                await bot.send_message(text=MESSAGES["pay_cancel"] % data["number_order"],
                                       chat_id=callback.from_user.id,
                                       parse_mode="HTML")
            except:
                await bot.send_message(text=MESSAGES["not_product"], chat_id=callback.from_user.id,
                                       reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
                await bot.send_message(text=MESSAGES["start_user_2"], chat_id=callback.from_user.id,
                                       reply_markup=generation_keyboard())

        else:
            await callback.message.edit_text(text=MESSAGES["pay_card_1"] % data["number_order"], parse_mode="HTML")
            await bot.send_message(
                text=MESSAGES["pay_card_2"] % (data["number_order"], matches, NUMBER_CARD[randrange(len(NUMBER_CARD))]),
                reply_markup=BUTTON_TYPES["BTN_MENU_HOME"], chat_id=callback.from_user.id, parse_mode="HTML")
            await bot.send_message(text=MESSAGES["pay_card_3"], reply_markup=BUTTON_TYPES["BTN_PROBLEMS"],
                                   chat_id=callback.from_user.id)
            await callback.answer()
            await state.finish()

            await asyncio.sleep(1800)
            await bot.send_message(text=MESSAGES["pay_cancel"] % data["number_order"], chat_id=callback.from_user.id,
                                   parse_mode="HTML")

        await state.finish()

    # ===================================================
    # ================= ЗАПУСК РАССЫЛКИ =================
    # ===================================================
    async def start_malling(message: Message):
        ADMIN_ID = db.get_all_info("ADMIN_ID")[0]
        if str(message.from_user.id) in str(ADMIN_ID):
            try:
                # РАССЫЛКА
                all_info_malling = db.get_all_malling()[-1]
                scheduler.add_job(send_m, trigger='cron', hour=all_info_malling[1][0:2],
                                  minute=all_info_malling[1][3:5],
                                  start_date=datetime.now(), kwargs={'bot': bot, "text_malling": all_info_malling[-1]},
                                  id=f"{message.message_id}_{message.from_user.id}")
                await bot.send_message(text=f"Рассылка зарегистрирована!\n\nВремя рассылки: {all_info_malling[1][0:5]}"
                                            f"\nТекст рассылки: {all_info_malling[-1]}\n\nId рассылки: <code>{message.message_id}_{message.from_user.id}</code>",
                                       chat_id=message.from_user.id, parse_mode="HTML")
            except:
                await bot.send_message(text="Рассылка была создана не верно!", chat_id=message.from_user.id)

    def start_malling_sql():
        all_info_malling = db.get_all_malling()[-1]
        scheduler.add_job(send_m, trigger='cron', hour=all_info_malling[1][0:2], minute=all_info_malling[1][3:5],
                          start_date=datetime.now(), kwargs={'bot': bot, "text_malling": all_info_malling[-1]},
                          id=f"{random.randint(0, 99999999)}")
        scheduler.start()

    # ===================================================
    # ================ ОСТАНОВКА РАССЫЛКИ ===============
    # ===================================================
    async def stop_malling(message: Message):
        ADMIN_ID = db.get_all_info("ADMIN_ID")[0]
        if str(message.from_user.id) in str(ADMIN_ID):
            try:
                scheduler.remove_job(f"{message.text[6:]}")
                await bot.send_message(text="Рассылка остановлена!", chat_id=message.from_user.id)
            except:
                await bot.send_message(text="Такой рассылки нет", chat_id=message.from_user.id)

    # ===================================================
    # =============== НЕИЗВЕСТНАЯ КОМАНДА ===============
    # ===================================================
    async def unknown_command(message: Message):
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id, message.from_user.username)
            captcha_text = await generation_captha(message)
            state = dp.current_state(user=message.from_user.id)
            await state.update_data(captha=captcha_text)
            await state.set_state(StatesUsers.all()[2])

        else:
            await bot.send_message(text=MESSAGES["start_user"], chat_id=message.from_user.id,
                                   reply_markup=BUTTON_TYPES["BTN_MENU_HOME"])
            await bot.send_message(text=MESSAGES["start_user_2"], chat_id=message.from_user.id,
                                   reply_markup=generation_keyboard())
            state = dp.current_state(user=message.from_user.id)
            await state.finish()

    # ===================================================
    # ================= ФУНКЦИЯ РАССЫЛКИ ================
    # ===================================================
    async def send_m(bot: bot, text_malling):
        all_id_users = db.get_all_user()
        for id_user in all_id_users:
            try:
                await bot.send_message(id_user[0], text_malling)
            except:
                ...

    # СТАРТ
    dp.register_message_handler(start_command,
                                lambda message: message.text == '/start' or message.text == 'Главное меню')
    dp.register_message_handler(start_malling, lambda message: message.text == '/start_m')
    dp.register_message_handler(stop_malling, lambda message: '/stop' in message.text)
    dp.register_callback_query_handler(start_command_inline, lambda callback: callback.data == "menu_home")

    dp.register_callback_query_handler(start_command_inline, lambda callback: callback.data == "menu_home",
                                       state=StatesUsers.STATE_0 | StatesUsers.STATE_1 | StatesUsers.STATE_3 | StatesUsers.STATE_4 | StatesUsers.STATE_5 | StatesUsers.STATE_6 | StatesUsers.STATE_7)
    dp.register_message_handler(start_command,
                                lambda message: message.text == '/start' or message.text == 'Главное меню',
                                state=StatesUsers.STATE_0 | StatesUsers.STATE_1 | StatesUsers.STATE_3 | StatesUsers.STATE_4 | StatesUsers.STATE_5 | StatesUsers.STATE_6 | StatesUsers.STATE_7)
    dp.register_message_handler(captha_start, state=StatesUsers.STATE_2)

    # РЕФЕРАЛЬНАЯ П
    dp.register_callback_query_handler(ref_program, lambda callback: callback.data == "ref")
    dp.register_callback_query_handler(not_buy, lambda callback: callback.data == "add_bot")

    # ПОСЛЕДНИЙ ЗАКАЗ
    dp.register_callback_query_handler(last_order, lambda callback: callback.data == "last_order")

    # МОИ БОТЫ
    dp.register_callback_query_handler(my_bot, lambda callback: callback.data == "my_bot")

    # ПОПОЛНЕНИЕ БАЛАНСА
    dp.register_callback_query_handler(add_balance, lambda callback: callback.data == "balance")
    dp.register_message_handler(input_balance, state=StatesUsers.STATE_0)
    dp.register_callback_query_handler(pay_card, lambda callback: callback.data == "card", state=StatesUsers.STATE_1)
    dp.register_callback_query_handler(pay_bitcoin, lambda callback: callback.data == "bitcoin",
                                       state=StatesUsers.STATE_1)
    dp.register_callback_query_handler(pay_ltc, lambda callback: callback.data == "ltc", state=StatesUsers.STATE_1)

    # ГОРОДА
    # dp.register_callback_query_handler(city, lambda callback: callback.data == "city")
    dp.register_callback_query_handler(district, lambda callback: 'а' <= callback.data.lower()[1:-2] <= 'ю')
    dp.register_callback_query_handler(products, state=StatesUsers.STATE_4)
    dp.register_callback_query_handler(card_selected, state=StatesUsers.STATE_5)
    dp.register_callback_query_handler(balance_user, state=StatesUsers.STATE_6)
    dp.register_callback_query_handler(buy_product, state=StatesUsers.STATE_7)

    # НЕИЗВЕСТНАЯ КОМАНДА
    dp.register_message_handler(unknown_command, content_types=["text"])

    event_loop.run_until_complete(start_bot(dp))


if __name__ == '__main__':
    pid = os.getpid()
    db.update_pid(pid)

    logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG)
    tokens = db.get_bot_token()[0].split("|")
    event_loop = asyncio.get_event_loop()

    for idx, token in enumerate(tokens):
        if idx != 0:
            try:
                bot_init(event_loop, token)
            except:
                ...

    event_loop.run_forever()
