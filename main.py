import telebot
from config import currencies, TOKEN
from extensions import Converter, APIException
from telebot import types

bot = telebot.TeleBot(TOKEN)

def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    for i in currencies.keys():
        if i != base:
            buttons.append(types.KeyboardButton(i.capitalize()))
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.send_message(message.chat.id, f"Добро пожаловать, {message.chat.username}!\n"
                                      f"Укажите сначала сумму перевода, а затем имя валюты и в какую валюту перевести.\n"
                                      f"Например: 100 рубль доллар\n"
                                      f"/start - перезапустить бота, /values - валюты, /help - помощь, /convert - конвертация")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, f"Чтобы работать с данным ботом, укажите сначала сумму перевода, а затем имя валюты и в какую валюту перевести.\n"
                                      f"Например: 100 рубль доллар")
    
@bot.message_handler(commands=['values'])
def send_values(message):
    text = "Доступные валюты:"
    for currency in currencies.keys():
        text = '\n'.join((text, currency))
    bot.reply_to(message, text)

@bot.message_handler(commands=['convert'])
def values(message: telebot.types.Message):
    text = "Выберите валюту, из которой нужно конвертировать:"
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)


def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = "Выберите валюту, в которую нужно конвертировать:"
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, quote_handler, base)

def quote_handler(message: telebot.types.Message, base):
    quote = message.text.strip().lower()
    text = "Выберите количество конвертируемой валюты:"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, quote)

def amount_handler(message: telebot.types.Message, base, quote):
    amount = message.text.strip()
    try:
        new_price = Converter.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f"Ошибка конвертации...\n{e}")
    else:
        text = f"Цена {amount} {base} в {quote} = {round(new_price, 4)}"
        bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    vals = message.text.lower().split()
    try:
        if len(vals) != 3:
            raise APIException("Количество параметров должно быть равно 3")
        base, quote, amount = map(str.lower, vals)
        total_base = Converter.get_price(*vals)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка ввода запроса.\n{e}")
    else:
        text =f"Цена {amount} {base} в {quote} = {round(total_base, 4)}"
        bot.send_message(message.chat.id, text)

bot.polling()
