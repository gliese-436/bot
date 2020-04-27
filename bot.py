import telebot
from telebot import types
import sqlite3
import qrcode
from PIL import Image, ImageDraw
import re

bot = telebot.TeleBot('995674544:AAFyQEr5fkXCLmjJKkC5eOQ-NrJZouVmXao')


@bot.message_handler(content_types=["contact"])
def phone(message):
    params = message.from_user.first_name, message.from_user.last_name, message.from_user.id, message.contact.phone_number
    conn = sqlite3.connect("mydatabase.db") 
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Clients WHERE id = {0}".format(message.from_user.id))
    results = cursor.fetchall()
    bot.send_message(message.chat.id, "спасибо", reply_markup=types.ReplyKeyboardRemove())
    if not results:
        cursor.execute("INSERT INTO Clients (first_name, last_name, id, phone_number) VALUES (?, ?, ?, ?)", params)
        conn.commit()
        conn.close()
        request_QR(message)   
        
@bot.message_handler(commands=['QR'])
def request_QR(message):
    markup = types.InlineKeyboardMarkup()
    button_QR = types.InlineKeyboardButton(text="Отправить QR-код", callback_data='add')
    markup.add(button_QR) 
    bot.send_message(message.chat.id, "Нажми на кнопку", reply_markup=markup)
    
@bot.message_handler     
@bot.callback_query_handler(func=lambda call: True)
def get_QR(call):
    if call.data == 'add':
        conn = sqlite3.connect("mydatabase.db") 
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number FROM Clients WHERE id = {0}".format(call.message.chat.id))
        results = str(cursor.fetchall()[0])
        phone_number = re.sub(r'[^0-9]', '', results)   
        image = qrcode.make(phone_number)
        image.save('qr_code_1.png')
        img = open('qr_code_1.png', 'rb')
        bot.send_photo(call.message.chat.id, img)
    
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'привет')
    conn = sqlite3.connect("mydatabase.db") # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Clients WHERE id = {0}".format(message.from_user.id))
    results = cursor.fetchall()
    if not results:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        keyboard.add(button_phone)
        bot.send_message(message.chat.id, "Отправь мне свой номер", reply_markup=keyboard)
    else:
        request_QR(message)    

bot.polling()
