import os
import telebot
import json

from telebot import types

TOKEN = '936426396:AAEwbo64h7Nf3lEJ56bW1ZoA3plMlyPl9VQ'
bot = telebot.TeleBot(TOKEN)

markup = types.ReplyKeyboardMarkup(row_width=3)
btn1 = types.KeyboardButton("Посмотреть список дел")
btn2 = types.KeyboardButton("Дабавить список дел")
btn3 = types.KeyboardButton("Очистить список дел")
btn4 = types.KeyboardButton("Выйти")
markup.add(btn1, btn2, btn3, btn4)


def read_from_file() -> dict:
    with open('data.json', 'r') as f:
        json_data = json.load(f)
        return json_data


def write_to_file(json_data: dict):
    with open('data.json', 'w') as f:
        json.dump(json_data, f)


if not os.path.exists('data.json'):
    write_to_file({})


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Привет', reply_markup=markup)


@bot.message_handler()
def handle_message(msg):
    chat_id = str(msg.chat.id)

    # Список дел
    if msg.text == btn1.text:
        json_data = read_from_file()
        todo_list = json_data.get(str(chat_id), [])
        if len(todo_list) <= 0:
            bot.send_message(chat_id, 'У тебя нет никаких дел', reply_markup=markup)
            return

        todo_body = 'Твой список дел:\n'
        for i, k in enumerate(todo_list):
            todo_body += f'{i}) {k}\n'
        bot.send_message(chat_id, todo_body)

        list_markup = types.ReplyKeyboardMarkup(row_width=3)
        edit_btn = types.KeyboardButton("Редактировать")
        delete_btn = types.KeyboardButton("Удалить")
        cancel_btn = types.KeyboardButton("Вернуться в главное меню")
        list_markup.add(edit_btn, delete_btn, cancel_btn)
        bot.send_message(chat_id, "Что необходиом сделать?", reply_markup=list_markup)

    if msg.text == "Редактировать":
        bot.send_message(chat_id, 'Вводи номер дела что-бы его редактивароть')
        bot.register_next_step_handler(msg, edit_todo_from_list)

    if msg.text == "Удалить":
        bot.send_message(chat_id, 'Вводи номер дела что-бы удалить его из списка')
        bot.register_next_step_handler(msg, delete_todo_from_list)

    if msg.text == "Вернуться в главное меню":
        bot.send_message(chat_id, 'Хорошо :)', reply_markup=markup)

    # Добавить дело
    if msg.text == btn2.text:
        bot.send_message(chat_id, 'Вводи что хочешь добавить в список')
        bot.register_next_step_handler(msg, add_todo_into_list)

    # Очистить список моих дел
    if msg.text == btn3.text:
        json_data = read_from_file()
        json_data[chat_id] = []
        write_to_file(json_data)
        bot.send_message(chat_id, 'Список очищен', reply_markup=markup)

    if msg.text == btn4.text:
        bot.send_message(chat_id, 'Всего доброго')


def add_todo_into_list(message):
    chat_id = str(message.chat.id)

    json_data = read_from_file()

    user_todo = json_data.get(chat_id, [])
    user_todo.append(message.text)
    json_data[chat_id] = user_todo

    write_to_file(json_data)

    bot.send_message(chat_id, 'Данные записаны', reply_markup=markup)


def delete_todo_from_list(message):
    chat_id = str(message.chat.id)
    json_data = read_from_file()

    user_todo = json_data.get(chat_id, [])

    try:
        todo_index = int(message.text)
    except ValueError:
        bot.send_message(chat_id, "Введи нормальное число!")
        return

    if todo_index < 0 or todo_index > len(user_todo):
        bot.send_message(chat_id, "Введи нормальное число!")
        return

    del user_todo[todo_index]
    json_data[chat_id] = user_todo
    write_to_file(json_data)

    bot.send_message(chat_id, "Дело удалено из твоего списка")


def edit_todo_from_list(message):
    chat_id = str(message.chat.id)
    json_data = read_from_file()
    user_todo = json_data.get(chat_id, [])

    try:
        todo_index = int(message.text)
    except ValueError:
        bot.send_message(chat_id, "Введи нормальное число!")
        return

    if todo_index < 0 or todo_index > len(user_todo):
        bot.send_message(chat_id, "Введи нормальное число! ")
        return

    def edit_todo(msg):
        user_todo[todo_index] = msg.text
        json_data[chat_id] = user_todo
        write_to_file(json_data)
        bot.send_message(chat_id, "Всё сохранено", reply_markup=markup)

    bot.send_message(chat_id, "Введите на что вы хотите поменять дело")
    bot.register_next_step_handler(message, edit_todo)


bot.polling()
