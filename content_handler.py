import telebot
from telebot import types
from aiogram.types.message import ContentType
import sqlite3

bot = telebot.TeleBot('TOKEN')
conn = sqlite3.connect('content.db', check_same_thread=False)
cursor = conn.cursor()

@bot.message_handler(content_types=["photo"])
def get_file_id(message):
    file_id = message.photo[3].file_id
    cursor.execute('INSERT INTO photo (file_id) values (?)', (file_id, ))
    conn.commit()

@bot.message_handler(content_types=["document"])
def get_file_id(message):
    file_id = message.document.file_id
    cursor.execute('INSERT INTO documents (file_id) values (?)', (file_id, ))
    conn.commit()

@bot.message_handler(content_types=["audio"])
def get_file_id(message):
    file_id = message.audio.file_id
    cursor.execute('INSERT INTO audio (file_id) values (?)', (file_id, ))
    conn.commit()
    

bot.infinity_polling(none_stop=True, interval=0)

