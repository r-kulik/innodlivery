from os import curdir
from sqlite3.dbapi2 import Cursor
import telebot
import config
import sources
import sqlite3

bot = telebot.TeleBot(config.token)

print("started working")

def add_user(user_id : int) -> None:
    database_connection = sqlite3.connect('data.db'); cursor = database_connection.cursor()
    status = 0; tickets = 0
    cursor.execute("INSERT INTO users VALUES ({}, {}, {});".format(user_id, status, tickets))
    database_connection.commit()
    database_connection.close()


def set_status(user_id : int, status : int) -> None:
    database_connection = sqlite3.connect("data.db"); cursor = database_connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id='{}')".format(user_id))
    fetchresult : tuple = cursor.fetchone()
    print(fetchresult)
    if fetchresult == (0,):
        database_connection.close()
        add_user(user_id)
    database_connection = sqlite3.connect("data.db"); cursor = database_connection.cursor()
    cursor.execute("UPDATE users SET status={} WHERE id={}".format(status, user_id))
    database_connection.commit()


def check_status(user_id : int) -> int:
    database_connection = sqlite3.connect('data.db'); cursor = database_connection.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    order_button = telebot.types.KeyboardButton(sources.order_button)
    accept_button = telebot.types.KeyboardButton(sources.picking_button)
    my_orders_button = telebot.types.KeyboardButton(sources.my_orders_button)
    markup.row(order_button)
    markup.row(accept_button, my_orders_button)
    bot.send_message(message.chat.id, sources.greeting, reply_markup=markup)

@bot.message_handler()
def handle_message(message):
    text : str = message.text
    user_id : int = message.chat.id
    if text == sources.order_button:
        bot.send_message(message.chat.id, sources.order_question, reply_markup=None)
        set_status(user_id, sources.input_order_status)
    elif text == sources.picking_button:
        pass
    elif text == sources.my_orders_button:
        pass
    else:
        user_status = check_status(user_id)
        if user_status == sources.input_order_status:
            pass


bot.polling()