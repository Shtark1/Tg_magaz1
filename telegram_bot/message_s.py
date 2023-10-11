from telegram_bot.utils import StatesUsers

# СООБЩЕНИЯ ОТ БОТА
start_message = "Привет"
start_message_2 = "выберите город"

start_admin_message = "Приветствую админ 👋"
not_command_message = "Такой команды нет\nПиши /start"

add_admin_message = """ID состоит только из чисел 
(его можно получить тут @username_to_id_bot)
<b>Вводи ID пользователя для ДОБАВЛЕНИЯ админа:</b>"""
del_admin_message = """ID состоит только из чисел 
(его можно получить тут @username_to_id_bot)
<b>Вводи ID пользователя для УДАЛЕНИЯ админа:</b>"""
not_admin_id_message = """Это не число, ID состоит только из чисел 
 (его можно получить тут @username_to_id_bot)
Вводи ID пользователя:"""

ref_message = """Делитесь своими ботами с друзьями и получайте 5% с каждого его оплаченного заказа.
Ваши боты:
У вас нету ботов!"""
add_bot_message = "Добавление бота доступно от 10-ти покупок"
not_order_message = "У вас нет подтверждённых заказов"
my_bot_message = "Ваши боты:\nУ вас нету ботов!"
captha_message = "Привет\nПожалуйста, решите капчу с цифрами на этом изображении, чтобы убедиться, что вы человек."
add_balance_message = "Введите сумму на которую вы хотите пополнить баланс"
not_balance_message = "Это не число\nПопробуй ввести снова:"
what_pay_messsage = "Чем вы будете оплачивать:"
pay_card_1_message = """✅ ВЫДАННЫЕ РЕКВИЗИТЫ ДЕЙСТВУЮТ 30 МИНУТ
✅ ВЫ ПОТЕРЯЕТЕ ДЕНЬГИ, ЕСЛИ ОПЛАТИТЕ ПОЗЖЕ
✅ ПЕРЕВОДИТЕ ТОЧНУЮ СУММУ. НЕВЕРНАЯ СУММА НЕ БУДЕТ ЗАЧИСЛЕНА.
✅ ОПЛАТА ДОЛЖНА ПРОХОДИТЬ ОДНИМ ПЛАТЕЖОМ.
✅ <b>ПРОБЛЕМЫ С ОПЛАТОЙ? ПЕРЕЙДИТЕ ПО ССЫЛКЕ : @doqo45 </b>
Предоставить чек об оплате и
ID:  %s
✅ С ПРОБЛЕМНОЙ ЗАЯВКОЙ ОБРАЩАЙТЕСЬ НЕ ПОЗДНЕЕ 24 ЧАСОВ С МОМЕНТА ОПЛАТЫ."""
pay_card_2_message = """✅Заявка на оплату <b>№%s</b>. Переведите на банковскую  карту <b>%s</b> рублей удобным для вас способом.  Важно пополнить ровную сумму.
<b><code>%s</code></b>
‼️ у вас есть 30 мин на оплату, после чего платёж не будет зачислен
‼️ перевёл неточную сумму - оплатил чужой заказ"""

pay_card_3_message = 'Если в течении часа средства не выдались автоматически то нажмите на кнопку - "Проблема с оплатой"'
pay_bitcoin_message = """Оплатите <code>%s</code> %s 
На адрес <b><code>%s</code></b>
Заявка на оплату <b>№%s</b>

‼️ у вас есть 30 мин на оплату, после чего платёж не будет зачислен
‼️ перевёл неточную сумму - оплатил чужой заказ"""
pay_cancel_message = "Ваша заявка <b>№%s</b> на пополнение отклонена!"

what_city_message = "Выберите город:"
district_message = "выберите район"
what_products_message = "Выберите продукт:"
card_selected_message = """Номер покупки <b>№%s</b>
Город: <b>%s</b>
Район: <b>%s</b> 
Товар и объем: <b>%s</b>
Для проведения оплаты нажмите на кнопку <b>ОПЛАТИТЬ</b>
После того, как Вы нажмете кнопку оплаты, у вас есть 30 минут на оплату"""
balance_user_message = """Ваш актуальный баланс 0 руб
Чем вы будете оплачивать?"""
not_product_message = "Товар закончился, зайдите позже"
edit_min_message = "Введите значение которое будет использоваться для минимального пополнения:"

MESSAGES = {
    "start_user": start_message,
    "start_user_2": start_message_2,
    "start_admin": start_admin_message,
    "not_command": not_command_message,
    "add_admin": add_admin_message,
    "del_admin": del_admin_message,
    "not_admin_id": not_admin_id_message,
    "ref": ref_message,
    "add_bot": add_bot_message,
    "not_order": not_order_message,
    "my_bot": my_bot_message,
    "captha": captha_message,
    "add_balance": add_balance_message,
    "not_balance": not_balance_message,
    "what_pay": what_pay_messsage,
    "pay_card_1": pay_card_1_message,
    "pay_card_2": pay_card_2_message,
    "pay_card_3": pay_card_3_message,
    "pay_bitcoin": pay_bitcoin_message,
    "pay_cancel": pay_cancel_message,
    "what_city": what_city_message,
    "what_district": district_message,
    "what_products": what_products_message,
    "card_selected": card_selected_message,
    "balance_user": balance_user_message,
    "not_product": not_product_message,
    "edit_min": edit_min_message,
}
