from os import curdir
from re import L
from sqlite3.dbapi2 import Connection, Cursor
import telebot
import config
import sources
import sqlite3
import random

bot = telebot.TeleBot(config.token)

print("started working")


def update_buffer(user_id : int, buffer_text : str) -> None:
    database_connection : Connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("UPDATE buffer SET buffer_text=\"{}\" WHERE user_id={}".format(buffer_text, user_id))
    database_connection.commit()
    database_connection.close()


def read_buffer(user_id : int) -> str:
    database_connection : Connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT buffer_text FROM buffer WHERE user_id={}".format(user_id))
    returnable_value = cursor.fetchone()[0]
    database_connection.close()
    return returnable_value


def get_tickets_quantity(user_id : int) -> int:
    database_conenction : Connection = sqlite3.connect(sources.database_file); cursor = database_conenction.cursor()
    cursor.execute("SELECT tickets FROM users WHERE id={}".format(user_id))
    returnable_value : int = cursor.fetchone()[0]
    return returnable_value


def increment_tickets(user_id : int) -> None:
    database_conenction : Connection = sqlite3.connect(sources.database_file); cursor = database_conenction.cursor()
    tickets_quantity = get_tickets_quantity(user_id)
    cursor.execute("UPDATE users SET tickets={} WHERE id={}".format(tickets_quantity + 1, user_id))
    database_conenction.commit()
    database_conenction.close()

def decrement_tickets(user_id : int) -> None:
    database_conenction : Connection = sqlite3.connect(sources.database_file); cursor = database_conenction.cursor()
    tickets_quantity = get_tickets_quantity(user_id)
    cursor.execute("UPDATE users SET tickets={} WHERE id={}".format(tickets_quantity - 1, user_id))
    database_conenction.commit()
    database_conenction.close()

def create_ticket(user_id : int, ticket_entity : str, ticket_reward : str, alias : str) -> None:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    '''
    !!!
    это настолько ебучий костыль, что его нужно переписать, иначе при большом числе пользователей возможны всякие
    колдоебки с айдишниками. но пока сойдет
    '''
    ticket_id : int = user_id + random.randint(1, 100000) 
    sqlexec_command = "INSERT INTO tickets VALUES ({}, {}, \"{}\", \"{}\", \"{}\")".format(ticket_id, user_id, ticket_entity, ticket_reward, alias)
    print(sqlexec_command)
    cursor.execute(sqlexec_command)
    database_connection.commit()
    database_connection.close()


def add_user(user_id : int) -> None:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    status = 0; tickets = 0
    cursor.execute("INSERT INTO users VALUES ({}, {}, {});".format(user_id, status, tickets))
    cursor.execute('INSERT INTO buffer VALUES ({}, "")'.format(user_id))
    database_connection.commit()
    database_connection.close()


def set_status(user_id : int, status : int) -> None:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id='{}')".format(user_id))
    fetchresult : tuple = cursor.fetchone()
    print(fetchresult)
    if fetchresult == (0,):
        database_connection.close()
        add_user(user_id)
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("UPDATE users SET status={} WHERE id={}".format(status, user_id))
    database_connection.commit()


def ticket_exists(ticket_id : int) -> bool:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT 1 FROM tickets WHERE ticket_id={}".format(ticket_id))
    try:
        returnable_value = cursor.fetchone()
        print(returnable_value)
        database_connection.close()
        return returnable_value is not None
    except Exception as e:
        print(e)
        return False

def delete_ticket(ticket_id : int) -> None:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT user_id FROM tickets WHERE ticket_id={}".format(ticket_id))
    user_id = cursor.fetchone()[0]
    decrement_tickets(user_id)
    cursor.execute("DELETE FROM tickets WHERE ticket_id={}".format(ticket_id))
    database_connection.commit()
    database_connection.close()

def check_status(user_id : int) -> int:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT status FROM users WHERE id={}".format(user_id));
    returnable_result = cursor.fetchone();
    # print(returnable_result[0])
    return returnable_result[0]


def get_user_orders(user_id : int) -> list:
    database_connection = sqlite3.connect(sources.database_file); cursor = database_connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE user_id={}".format(user_id))
    returnable_array = list(cursor.fetchall())
    database_connection.close()
    return returnable_array

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    callback_request = call.data.split()
    if callback_request[0] == 'delete':
        if ticket_exists(callback_request[1]):
            delete_ticket(callback_request[1])
            bot.delete_message(call.message.chat.id, call.message.message_id)
            
        else:
            bot.answer_callback_query(callback_query_id=call.id, text='Order has been already deleted')  
    
    


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
        set_status(user_id, sources.input_order_status)
        if get_tickets_quantity(user_id) < 5:
            markup = telebot.types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, sources.order_question, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, sources.many_tickets_error_text)
            set_status(user_id, sources.main_menu)
            start(message)
    elif text == sources.picking_button:
        pass
    elif text == sources.my_orders_button:
        user_orders : list = get_user_orders(user_id);
        if len(user_orders) == 0:
            bot.send_message(user_id, sources.no_orders_text)
            return 0
        for order in user_orders:
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text=sources.delete_text, callback_data="delete {}".format(order[0])))
            bot.send_message(user_id, sources.ticket_format.format(order[0], order[2], order[3], order[4]), reply_markup=markup)
    else:
        user_status = check_status(user_id)
        if user_status == sources.input_order_status:
            ticket_entity : str = message.text;
            update_buffer(user_id, ticket_entity);
            bot.send_message(user_id, sources.reward_question)
            set_status(user_id, sources.input_order_reward_status)
        if user_status == sources.input_order_reward_status:
            ticket_reward : str = message.text;
            ticket_entity = read_buffer(user_id);
            alias : str = message.from_user.username
            create_ticket(user_id, ticket_entity, ticket_reward, alias)
            increment_tickets(user_id)
            bot.send_message(user_id, sources.ticket_created_message)
            set_status(user_id, sources.main_menu)
            start(message)

bot.polling()