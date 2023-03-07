import telebot
from telebot import types
from aiogram.types.message import ContentType
import sqlite3
import time

bot = telebot.TeleBot('TOKEN')
conn_to_users = sqlite3.connect('users.db', check_same_thread=False)
cursor_to_users = conn_to_users.cursor()
conn_to_content = sqlite3.connect('content.db', check_same_thread=False)
cursor_to_content = conn_to_content.cursor()

#проверка оплаты курса мм инь
def check_user_paid_mm_in(user_id):
    cursor_to_users.execute(f'select course_paid_mm_in from users where user_id = {user_id}')
    return cursor_to_users.fetchone()[0] == 1

#проверка оплаты курса мм янь
def check_user_paid_mm_yang(user_id):
    cursor_to_users.execute(f'select course_paid_mm_yang from users where user_id = {user_id}')
    return cursor_to_users.fetchone()[0] == 1

def price_mm_in(user_id):
    cursor_to_users.execute(f'select discount_for_mm_in from users where user_id = {user_id}')
    discount = cursor_to_users.fetchone()[0]
    price = 10000 - ((10000*(discount*100))/10000)
    return int(price)

#проверка существования пользователя в базе, добавляет его, если пользователь впервые
def new_user(user_id, user_name, user_surname, username):
    cursor_to_users.execute('select * from users where user_id = ?', (user_id,))
    if cursor_to_users.fetchone() is None:      
        cursor_to_users.execute('''INSERT INTO users (
                        user_id, user_name, user_surname, username, course_paid_mm_in,
                        course_paid_mm_yang, discount_for_mm_in, discount_for_mm_yang)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (user_id, user_name, user_surname, username, 0, 0, 0, 0))
        conn_to_users.commit()

#генерация клавиатуры с произвольным кол-вом кнопок
def keyboard_render(num_of_buttons, text_of_buttons:list):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for i in range(num_of_buttons):
        keyboard.add(types.KeyboardButton(text=text_of_buttons[i]))
    return keyboard

#обращение к базе данных с контентом курса
def content_from_db(num_of_message, course, content):
    cursor_to_content.execute(f'select {content} from {course} where id = {num_of_message}')
    return cursor_to_content.fetchone()[0]

#генерация клавиатур курсов (она существует отдельно, поскольку генерация кнопок через цикл ломает функционал размещения заданного количества кнопок в строке
#и при относительно большом их количестве как здесь, клавиатура заслоняет большую часть текста)
def course_mm_in_keyboard(paid=False):
    if paid == True:
        kb = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        btn_1 = types.KeyboardButton(text='ММ Инь Урок 1')
        btn_2 = types.KeyboardButton(text='ММ Инь Урок 2')
        btn_3 = types.KeyboardButton(text='ММ Инь Урок 3')
        btn_4 = types.KeyboardButton(text='ММ Инь Урок 4')
        btn_5 = types.KeyboardButton(text='ММ Инь Урок 5')
        btn_6 = types.KeyboardButton(text='ММ Инь Урок 6')
        btn_7 = types.KeyboardButton(text='Главное меню')
        kb.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
        return kb
    else:
        kb = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        btn_1 = types.KeyboardButton(text='ММ Инь Урок 1')
        btn_2 = types.KeyboardButton(text='ММ Инь Урок 2')
        btn_3 = types.KeyboardButton(text='ММ Инь Урок 3')
        btn_4 = types.KeyboardButton(text='ММ Инь Урок 4')
        btn_5 = types.KeyboardButton(text='ММ Инь Урок 5')
        btn_6 = types.KeyboardButton(text='ММ Инь Урок 6')
        btn_7 = types.KeyboardButton(text='Главное меню')
        btn_8 = types.KeyboardButton(text='Купить курс ММ Инь')
        kb.add(btn_8, btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
        return kb
    
def course_mm_yang_keyboard(paid=False):
    if paid == True:
        kb = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        btn_1 = types.KeyboardButton(text='ММ Ян Урок 1')
        btn_2 = types.KeyboardButton(text='ММ Ян Урок 2')
        btn_3 = types.KeyboardButton(text='ММ Ян Урок 3')
        btn_4 = types.KeyboardButton(text='ММ Ян Урок 4')
        btn_5 = types.KeyboardButton(text='ММ Ян Урок 5')
        btn_6 = types.KeyboardButton(text='ММ Ян Урок 6')
        btn_7 = types.KeyboardButton(text='Главное меню')
        kb.add(btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
        return kb
    else:
        kb = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        btn_1 = types.KeyboardButton(text='ММ Ян Урок 1')
        btn_2 = types.KeyboardButton(text='ММ Ян Урок 2')
        btn_3 = types.KeyboardButton(text='ММ Ян Урок 3')
        btn_4 = types.KeyboardButton(text='ММ Ян Урок 4')
        btn_5 = types.KeyboardButton(text='ММ Ян Урок 5')
        btn_6 = types.KeyboardButton(text='ММ Ян Урок 6')
        btn_7 = types.KeyboardButton(text='Главное меню')
        btn_8 = types.KeyboardButton(text='Купить')
        kb.add(btn_8, btn_1, btn_2, btn_3, btn_4, btn_5, btn_6, btn_7)
        return kb
        
#функция, обращающаяся к бд в случае оплаты или применения промокода
def course_paid(invoice, user_id):
    if invoice == 'mm_in_paid':
        cursor_to_users.execute(f'UPDATE users SET course_paid_mm_in = {1} WHERE user_id = {user_id}')
        conn_to_users.commit()
    elif invoice == 'mm_yang_paid':
        cursor_to_users.execute(f'UPDATE users SET course_paid_mm_yang = {1} WHERE user_id = {user_id}')
        conn_to_users.commit()
    elif invoice == 'promo_mm_in':
        cursor_to_content.execute(f'SELECT promocode_mm_in FROM promo WHERE buy_mm_in = {0}')
        promocode = cursor_to_content.fetchone()[0]
        cursor_to_content.execute('UPDATE promo SET buy_mm_in = ? WHERE promocode_mm_in = ?', (1, promocode))
        conn_to_content.commit()
        bot.send_message(user_id, f'Ваш подарочный промокод: <b>{promocode}</b>', 'HTML')
    elif invoice == 'promo_mm_yang':
        cursor_to_content.execute(f'SELECT promocode_mm_yang FROM promo WHERE buy_mm_yang = {0}')
        promocode = cursor_to_content.fetchone()[0]
        cursor_to_content.execute('UPDATE promo SET buy_mm_yang = ? WHERE promocode_mm_yang = ?', (1, promocode))
        conn_to_content.commit()
        bot.send_message(user_id, f'Ваш подарочный промокод: <b>{promocode}</b>', 'HTML')

def send_music(message):
    audio = []
    for i in range(1, 16):
        cursor_to_content.execute(f'select file_id from audio where id = {i}')
        audio.append(cursor_to_content.fetchone()[0])
    bot.send_audio(message.from_user.id, audio[0], '''Музыка для медитаций. В ней присутствуют звуки природы,
                                                        разных инструментов, и иногда можно услышать чьи-то голоса.
                                                        (Все права на музыку принадлежат ее авторам)''')
    bot.send_media_group(message.from_user.id, media=[types.InputMedia(type='audio', media=audio[1]),
                                                      types.InputMedia(type='audio', media=audio[2]),
                                                      types.InputMedia(type='audio', media=audio[3]),
                                                      types.InputMedia(type='audio', media=audio[4])])
    bot.send_audio(message.from_user.id, audio[5], '''Эмбиент. Для тех, кто не знает - это стиль электронной музыки, основанный на модуляциях звукового тембра.
                                                        Обычно это можно услышать на фоне в спа-салонах на фоне.
                                                        (Все права на музыку принадлежат ее авторам)''')
    bot.send_media_group(message.from_user.id, media=[types.InputMedia(type='audio', media=audio[6]),
                                                      types.InputMedia(type='audio', media=audio[7]),
                                                      types.InputMedia(type='audio', media=audio[8]),
                                                      types.InputMedia(type='audio', media=audio[9])])
    bot.send_audio(message.from_user.id, audio[10], '''Легкий джаз. Вы можете использовать его, если любите что-то чуть более яркое,
                                                         и не хотите сильно погружаться в себя. Вся эта музыка - моя собственная выборка,
                                                         Вы можете собрать подходящий для Вас плейлист самостоятельно. 
                                                         (Все права на музыку принадлежат ее авторам)''')
    bot.send_media_group(message.from_user.id, media=[types.InputMedia(type='audio', media=audio[11]),
                                                      types.InputMedia(type='audio', media=audio[12]),
                                                      types.InputMedia(type='audio', media=audio[13]),
                                                      types.InputMedia(type='audio', media=audio[14])])

#стартовый хендлер
@bot.message_handler(commands=['start'])
def start(message):
    user_id, user_name, user_surname, username = message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username
    kb = keyboard_render(2, ['ММ Инь', 'ММ Ян'])
    bot.send_message(message.chat.id, 'Выберете курс. Также, если у вас есть подарочный промокод, вы можете ввести его здесь.', reply_markup=kb)
    new_user(user_id, user_name, user_surname, username)

#хендлер проверки промокода
@bot.message_handler(func= lambda message : message.text[0:2] == 'IN')
@bot.message_handler(func= lambda message : message.text[0:2] == 'YA')
def input_promo(message):
    promo = message.text
    if promo[0:2] == 'IN':
        cursor_to_content.execute('SELECT used_mm_in FROM promo WHERE promocode_mm_in = ?', (promo, ))
        if cursor_to_content.fetchone()[0] == 0:
            cursor_to_content.execute('UPDATE promo SET used_mm_in = ? WHERE promocode_mm_in = ?', (1, promo))
            conn_to_content.commit()
            course_paid('mm_in_paid', message.from_user.id)
            bot.send_message(message.from_user.id, 'Промокод принят, теперь вам доступна полная версия курса ММ Инь!')
        else:
            bot.send_message(message.from_user.id, 'Недействительный промокод!')
    elif promo[0:2] == 'YA':
        cursor_to_content.execute('SELECT used_mm_yang FROM promo WHERE promocode_mm_yang = ?', (promo, ))
        if cursor_to_content.fetchone()[0] == 0:
            cursor_to_content.execute('UPDATE promo SET used_mm_yang = ? WHERE promocode_mm_yang = ?', (1, promo))
            conn_to_content.commit()
            course_paid('mm_yang_paid', message.from_user.id)
            bot.send_message(message.from_user.id, 'Промокод принят, теперь вам доступна полная версия курса ММ Ян!')
        else:
            bot.send_message(message.from_user.id, 'Недействительный промокод!')

#хендлер мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь')
def course_mm_in_menu(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = keyboard_render(3, ['К курсу ММ Инь', 'Купить ММ Инь в подарок', 'Главное меню'])
        bot.send_message(message.chat.id, 'Выберете', reply_markup=kb)
    else:
        kb = keyboard_render(4, ['Попробовать ММ Инь бесплатно', 'Купить курс ММ Инь',
                                 'Купить ММ Инь в подарок', 'Главное меню'])
        bot.send_message(message.chat.id, 'Выберете', reply_markup=kb)

#хендлер перехода к курсу мм инь
@bot.message_handler(func= lambda message : message.text == 'К курсу ММ Инь')
def course_mm_in(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
    else:
        kb = course_mm_in_keyboard()
    bot.send_message(message.from_user.id, content_from_db(num_of_message=1, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
    bot.send_message(message.from_user.id, content_from_db(num_of_message=2, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
    bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=2, course='content_mm_in', content='photo'), reply_markup=kb)

#хендлер первого урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 1')
def mm_in_step_1(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=3, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=4, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=5, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=5, course='content_mm_in', content='photo'), reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=5, course='content_mm_in', content='document'), reply_markup=kb)
    else:
        kb = course_mm_in_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=3, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=4, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=5, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=5, course='content_mm_in', content='photo'), reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=5, course='content_mm_in', content='document'), reply_markup=kb)
        bot.send_message(message.from_user.id, text=content_from_db(1, course='questions', content='question_mm_in'),reply_markup=kb, parse_mode='HTML')

#хендлер принимающий ответ на вопрос после уроков 1-3 в курсе мм инь
@bot.message_handler(func= lambda message : message.text[0:12].lower() == 'ответ мм инь')
def answer_mm_in(message):
    cursor_to_users.execute(f'select discount_for_mm_in from users where user_id = {message.from_user.id}')
    if cursor_to_users.fetchone()[0] < 15:
        cursor_to_users.execute(f'update users set discount_for_mm_in = discount_for_mm_in + 5 where user_id = {message.from_user.id}')
        conn_to_users.commit()
        cursor_to_users.execute(f'select discount_for_mm_in from users where user_id = {message.from_user.id}')
        discount = cursor_to_users.fetchone()[0]
        bot.send_message(message.from_user.id, f'Спасибо за ваш ответ! Ваша накапливаемая скидка на данный момент составляет: {discount}%')
    else:
        cursor_to_users.execute(f'select discount_for_mm_in from users where user_id = {message.from_user.id}')
        discount = cursor_to_users.fetchone()[0]
        bot.send_message(message.from_user.id, f'Вы уже получили максимально возможную скидку, которая составляет {discount}%')    

#хендлер второго урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 2')
def mm_in_step_2(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=6, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=7, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=7, course='content_mm_in', content='photo'), reply_markup=kb)
        send_music(message)
    else:
        kb = course_mm_in_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=6, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=7, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=7, course='content_mm_in', content='photo'), reply_markup=kb)
        send_music(message)
        bot.send_message(message.from_user.id, text=content_from_db(2, course='questions', content='question_mm_in'),reply_markup=kb, parse_mode='HTML')

#хендлер третьего урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 3')
def mm_in_step_3(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=8, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=9, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=9, course='content_mm_in', content='photo'), reply_markup=kb)
    else:
        kb = course_mm_in_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=8, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=9, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=9, course='content_mm_in', content='photo'), reply_markup=kb)
        bot.send_message(message.from_user.id, text=content_from_db(3, course='questions', content='question_mm_in'),reply_markup=kb, parse_mode='HTML')

#хендлер четвёртого урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 4')
def mm_in_step_4(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=10, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=11, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=11, course='content_mm_in', content='photo'), reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=11, course='content_mm_in', content='document'), reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')

#хендлер пятого урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 5')
def mm_in_step_5(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=12, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=13, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=13, course='content_mm_in', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=14, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=14, course='content_mm_in', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=15, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=15, course='content_mm_in', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=16, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=16, course='content_mm_in', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=17, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=17, course='content_mm_in', content='text'), reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')

#хендлер шестого урока мм инь
@bot.message_handler(func= lambda message : message.text == 'ММ Инь Урок 6')
def mm_in_step_6(message):
    if check_user_paid_mm_in(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=18, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=19, course='content_mm_in', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=20, course='content_mm_in', content='photo'),
                       caption=content_from_db(num_of_message=20, course='content_mm_in', content='text'), reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')

#хендлер покупки курса мм инь в подарок
@bot.message_handler(func= lambda message : message.text == 'Купить ММ Инь в подарок')
def gift_mm_in(message):
    price = types.LabeledPrice(label='Подарочный промокод курса ММ Инь', amount=10000)
    bot.send_invoice(message.from_user.id,
    title='Подарочный промокод курса ММ Инь',
    description='Подарочный промокод курса ММ Инь',
    provider_token='381764678:TEST:48483',
    currency='rub',
    prices=[price],
    invoice_payload='promo_mm_in')

#хендлер кнопки попробовать мм инь бесплатно, который ведёт так же как и хендлер 'к курсу'
@bot.message_handler(func= lambda message : message.text == 'Попробовать ММ Инь бесплатно')
def trial_mm_in(message):
    course_mm_in(message)

@bot.message_handler(func= lambda message : message.text == 'Купить курс ММ Инь')
def buy_mm_in(message):
    price = types.LabeledPrice(label='Курс медитативной мастурбации Инь', amount=price_mm_in(message.from_user.id))
    if check_user_paid_mm_in(message.from_user.id) == False:
        bot.send_invoice(message.from_user.id,
        title='Курс медитативной мастурбации Инь',
        description='Курс по медитативной мастурбации Инь',
        provider_token='381764678:TEST:48483',
        currency='rub',
        prices=[price],
        invoice_payload='mm_in_paid')
    else:
        bot.send_message(message.from_user.id, 'Вы уже приобрели курс ММ Инь!')

@bot.message_handler(func= lambda message : message.text == 'Купить курс ММ Ян')
def buy_mm_yang(message):
    price = types.LabeledPrice(label='Курс медитативной мастурбации Ян', amount=price_mm_in(message.from_user.id))
    if check_user_paid_mm_yang(message.from_user.id) == False:
        bot.send_invoice(message.from_user.id,
        title='Курс медитативной мастурбации Ян',
        description='Курс по медитативной мастурбации Ян',
        provider_token='381764678:TEST:48483',
        currency='rub',
        prices=[price],
        invoice_payload='mm_yang_paid')
    else:
        bot.send_message(message.from_user.id, 'Вы уже приобрели курс ММ Ян!')


@bot.message_handler(func= lambda message : message.text == 'ММ Ян')
def course_mm_yang(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = keyboard_render(3, ['К курсу ММ Ян', 'Купить ММ Ян в подарок', 'Главное меню'])
        bot.send_message(message.chat.id, 'Выберете', reply_markup=kb)
    else:
        kb = keyboard_render(4, ['Попробовать ММ Ян бесплатно', 'Купить курс ММ Ян',
                                 'Купить ММ Ян в подарок', 'Главное меню'])
        bot.send_message(message.chat.id, 'Выберете', reply_markup=kb)

@bot.message_handler(func= lambda message : message.text == 'К курсу ММ Ян')
def course_mm_yang(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(paid=True)
    else:
        kb = course_mm_yang_keyboard()
    bot.send_message(message.from_user.id, content_from_db(num_of_message=1, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
    bot.send_message(message.from_user.id, content_from_db(num_of_message=2, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
    bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=2, course='content_mm_yang', content='photo'), reply_markup=kb)

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 1')
def mm_yang_step_1(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=3, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=4, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=5, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=5, course='content_mm_yang', content='photo'), reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=5, course='content_mm_yang', content='document'), reply_markup=kb)
    else:
        kb = course_mm_yang_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=3, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=4, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=5, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=5, course='content_mm_yang', content='photo'), reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=5, course='content_mm_yang', content='document'), reply_markup=kb)
        bot.send_message(message.from_user.id, text=content_from_db(1, course='questions', content='question_mm_yang'),reply_markup=kb, parse_mode='HTML')

@bot.message_handler(func= lambda message : message.text[0:11].lower() == 'ответ мм ян')
def answer_mm_in(message):
    cursor_to_users.execute(f'select discount_for_mm_yang from users where user_id = {message.from_user.id}')
    if cursor_to_users.fetchone()[0] < 15:
        cursor_to_users.execute(f'update users set discount_for_mm_yang = discount_for_mm_yang + 5 where user_id = {message.from_user.id}')
        conn_to_users.commit()
        cursor_to_users.execute(f'select discount_for_mm_yang from users where user_id = {message.from_user.id}')
        discount = cursor_to_users.fetchone()[0]
        bot.send_message(message.from_user.id, f'Спасибо за ваш ответ! Ваша накапливаемая скидка на данный момент составляет: {discount}%')
    else:
        cursor_to_users.execute(f'select discount_for_mm_yang from users where user_id = {message.from_user.id}')
        discount = cursor_to_users.fetchone()[0]
        bot.send_message(message.from_user.id, f'Вы уже получили максимально возможную скидку, которая составляет {discount}%')

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 2')
def mm_yang_step_2(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=6, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=7, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=7, course='content_mm_yang', content='photo'), reply_markup=kb)
        send_music(message)
    else:
        kb = course_mm_yang_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=6, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=7, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=7, course='content_mm_yang', content='photo'), reply_markup=kb)
        send_music(message)
        bot.send_message(message.from_user.id, text=content_from_db(2, course='questions', content='question_mm_yang'),reply_markup=kb, parse_mode='HTML')

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 3')
def mm_yang_step_3(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=8, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=9, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=9, course='content_mm_yang', content='photo'), reply_markup=kb)
    else:
        kb = course_mm_yang_keyboard()
        bot.send_message(message.from_user.id, content_from_db(num_of_message=8, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=9, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=9, course='content_mm_yang', content='photo'), reply_markup=kb)
        bot.send_message(message.from_user.id, text=content_from_db(3, course='questions', content='question_mm_yang'),reply_markup=kb, parse_mode='HTML')

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 4')
def mm_yang_step_4(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=10, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=11, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(message.from_user.id, photo=content_from_db(num_of_message=11, course='content_mm_yang', content='photo'), reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 5')
def mm_yang_step_5(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_in_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=12, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=13, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=13, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=14, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=14, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=15, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=15, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=16, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=16, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=17, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=17, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_photo(chat_id=message.from_user.id, photo=content_from_db(num_of_message=18, course='content_mm_yang', content='photo'),
                       caption=content_from_db(num_of_message=17, course='content_mm_yang', content='text'), reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=19, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_document(message.from_user.id, document=content_from_db(num_of_message=19, course='content_mm_yang', content='document'), reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')

@bot.message_handler(func= lambda message : message.text == 'ММ Ян Урок 6')
def mm_yang_step_6(message):
    if check_user_paid_mm_yang(message.from_user.id) == True:
        kb = course_mm_yang_keyboard(paid=True)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=20, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
        bot.send_message(message.from_user.id, content_from_db(num_of_message=21, course='content_mm_yang', content='text'), parse_mode='HTML', reply_markup=kb)
    else:
        bot.send_message(message.from_user.id, 'Этот урок находится в платной части курса! Для доступа к его содержимому необходимо преобрести курс.')
        
@bot.message_handler(func= lambda message : message.text == 'Купить ММ Ян в подарок')
def gift_mm_yang(message):
    price = types.LabeledPrice(label='Подарочный промокод курса ММ Ян', amount=10000)
    bot.send_invoice(message.from_user.id,
    title='Подарочный промокод курса ММ Ян',
    description='Подарочный промокод курса ММ Ян',
    provider_token='381764678:TEST:48483',
    currency='rub',
    prices=[price],
    invoice_payload='promo_mm_yang')

@bot.message_handler(func= lambda message : message.text == 'Попробовать ММ Ян бесплатно')
def trial_mm_yang(message):
    course_mm_yang(message)

@bot.message_handler(func= lambda message : message.text == 'Главное меню')
def back_to_main(message):
    start(message)

#обработчики успешной оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    course_paid(pre_checkout_query.invoice_payload, pre_checkout_query.from_user.id)

@bot.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
def process_successful_payment(message: types.Message):
    start(message)

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            time.sleep(0.3)
