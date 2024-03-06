import telebot
from telebot import types
import sqlite3
from random import randint
import datetime

bot = telebot.TeleBot('ENTER BOT TOKEN HERE')
status = 'wait'
mode = ''
current_id = ''
value = ''


@bot.message_handler(commands=['start'])
def welcome(message):
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO users (tg_id, status, balance, date_of_last_take, message_count, prefix) '
                f'SELECT {message.chat.id}, "Участник", 0, NULL, 0, 0 '
                f'WHERE NOT EXISTS (SELECT 1 FROM users WHERE tg_id = {message.chat.id});'
                )
    cur.execute(f'UPDATE users '
                f'SET message_count = message_count + 1 '
                f'WHERE tg_id = {message.chat.id};')
    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("профиль", callback_data='profile')
    btn2 = types.InlineKeyboardButton("help", callback_data='help')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     f"Привет, добро пожаловать в наш маркет 🗝 \n\n"
                     f"Тут ты сможешь воспользоваться услугами нашего магазина 🖤\n\n"
                     f"• Для начала работы с ботом - нажми на кнопку «профиль» в этом чате\n\n"
                     f"• Если у тебя есть какие-либо вопросы нажми на кнопку «help»",
                     parse_mode='html',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global mode, value
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    if callback.data == 'profile':
        cur.execute(
            f'SELECT status, balance, diamonds, message_count, prefix FROM users WHERE tg_id = {callback.message.chat.id}')
        row = cur.fetchone()
        status, balance, diamonds, message_count, prefix = row
        if prefix == 0:
            prefix = 'Нет'
        else:
            prefix = 'Есть'
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton('Магазин', callback_data='shop')
        btn2 = types.InlineKeyboardButton(text="На охоту", callback_data='go_to_hunt')
        btn3 = types.InlineKeyboardButton('Назад', callback_data='main_menu')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text=f'🖲ID: {callback.message.chat.id}\n'
                 f'💼Статус: <b>{status}</b>\n'
                 f'🗝Баланс: <b>{balance}</b>\n'
                 f'💎Алмазы: <b>{diamonds}</b>\n'
                 f'💌Сообщений: <b>{message_count}</b>\n'
                 f'⚜️Префикс: <b>{prefix}</b>',
            reply_markup=markup, parse_mode='html')
    elif callback.data == 'help':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn2 = types.InlineKeyboardButton(text="Разработчик бота", url='t.me/parzival2303')
        btn1 = types.InlineKeyboardButton(text="Главный администратор", url='t.me/uegegs66')
        btn3 = types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text="Для начала работы с ботом, нажмите кнопку «профиль» внизу этого сообщения.\n\n"
                 "По другим вопросам можно обратиться в поддержку",
            reply_markup=markup
        )
    elif callback.data == 'shop':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Внутреигровые вещи👻', callback_data='prefix')
        btn2 = types.InlineKeyboardButton(text='Алмазы💎', url='t.me/uegegs66')
        btn3 = types.InlineKeyboardButton('Назад', callback_data='profile')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(
            message_id=callback.message.message_id,
            chat_id=callback.message.chat.id,
            text='Выберите категорию:',
            reply_markup=markup
        )
    elif callback.data == 'main_menu':
        welcome(message=callback.message)
    elif callback.data == 'drop_balance':
        mode = 'drop_next'
        value = 'balance'
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Введите Telegram ID того пользователя, '
                                   'которому вы хотите пополнить баланс:', reply_markup=markup)
    elif callback.data == 'drop_diamonds':
        mode = 'drop_next'
        value = 'diamonds'
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Введите Telegram ID того пользователя, '
                                   'которому вы хотите начислить алмазы:', reply_markup=markup)
    elif callback.data == 'drop':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Баланс🗝', callback_data='drop_balance')
        btn2 = types.InlineKeyboardButton(text='Алмазы💎', callback_data='drop_diamonds')
        btn3 = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Выберите валюту для пополнения:', reply_markup=markup)

    elif callback.data == 'take_balance':
        mode = 'take_next'
        value = 'balance'
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Введите Telegram ID того пользователя, '
                                   'у которого вы хотите забрать баланс:', reply_markup=markup)
    elif callback.data == 'take_diamonds':
        mode = 'take_next'
        value = 'diamonds'
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Введите Telegram ID того пользователя, '
                                   'у которого вы хотите забрать алмазы:', reply_markup=markup)
    elif callback.data == 'take':

        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Баланс🗝', callback_data='take_balance')
        btn2 = types.InlineKeyboardButton(text='Алмазы💎', callback_data='take_diamonds')
        btn3 = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                              text='Выберите валюту для изъятия:', reply_markup=markup)

    elif callback.data == 'cancel':
        mode = ''
        welcome(message=callback.message)
    elif callback.data == 'prefix':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Префикс', callback_data='prefix_buy')
        btn2 = types.InlineKeyboardButton(text='Назад', callback_data='shop')
        markup.add(btn1, btn2)
        bot.edit_message_text('Выберите продукт', message_id=callback.message.message_id,
                              chat_id=callback.message.chat.id, reply_markup=markup)
    elif callback.data == 'prefix_buy':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text='Купить', callback_data='prefix_buy_load')
        btn2 = types.InlineKeyboardButton(text="Назад", callback_data='prefix')
        markup.add(btn1, btn2)
        bot.edit_message_text('Купить Префикс за 250🗝?', chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id, reply_markup=markup)
    elif callback.data == 'prefix_buy_load':
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()
        cur.execute(f'SELECT balance FROM users WHERE tg_id = {callback.message.chat.id}')
        balance = cur.fetchone()[0]
        if balance < 250:
            cur.execute(f'SELECT prefix FROM users WHERE tg_id = {callback.message.chat.id}')
            prefix = cur.fetchone()[0]
            if prefix == 1:
                lol = types.InlineKeyboardMarkup(row_width=1)
                btn1 = types.InlineKeyboardButton(text='Назад', callback_data='shop')
                lol.add(btn1)
                bot.edit_message_text(text='У вас уже куплен Префикс', message_id=callback.message.message_id,
                                      chat_id=callback.message.chat.id, reply_markup=lol)
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                btn = types.InlineKeyboardButton(text='Назад', callback_data='shop')
                markup.add(btn)
                bot.edit_message_text('У вас недостаточно 🗝 на баласе!', message_id=callback.message.message_id,
                                      chat_id=callback.message.chat.id, reply_markup=markup)
        else:
            cur.execute(f'SELECT prefix FROM users WHERE tg_id = {callback.message.chat.id}')
            prefix = cur.fetchone()[0]
            if prefix == 1:
                lol = types.InlineKeyboardMarkup(row_width=1)
                btn1 = types.InlineKeyboardButton(text='Назад', callback_data='shop')
                lol.add(btn1)
                bot.edit_message_text(text='У вас уже куплен Префикс', message_id=callback.message.message_id,
                                      chat_id=callback.message.chat.id, reply_markup=lol)
            else:
                cur.execute(f'UPDATE users '
                            f'SET balance = balance - 250 '
                            f'WHERE tg_id = {callback.message.chat.id};')
                cur.execute(f'UPDATE users '
                            f'SET prefix = 1 '
                            f'WHERE tg_id = {callback.message.chat.id};')
                markup = types.InlineKeyboardMarkup(row_width=1)
                btn1 = types.InlineKeyboardButton(text='Назад', callback_data='shop')
                markup.add(btn1)
                bot.edit_message_text('Поздравляем! Вы успешно преобрели Префикс!',
                                      message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                      reply_markup=markup)
    elif callback.data == 'go_to_hunt':
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton(text='Назад', callback_data='profile')
        markup.add(btn)
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()
        cur.execute(f'SELECT date_of_last_take FROM users WHERE tg_id = {callback.message.chat.id}')
        date_of_last_take = cur.fetchone()
        if date_of_last_take[0] is None or datetime.datetime.fromisoformat(
                date_of_last_take[0]).date() < datetime.date.today():
            random_coins = randint(1, 3)
            cur.execute(f"UPDATE users "
                        f"SET date_of_last_take = date('now', 'localtime'), "
                        f"    balance = balance + {random_coins} "
                        f"WHERE tg_id = {callback.message.chat.id};")

            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                  text=f'Вы получили {random_coins} 🗝', reply_markup=markup)

        else:
            bot.edit_message_text(message_id=callback.message.message_id, chat_id=callback.message.chat.id,
                                  text="С прошлой охоты ещё не прошли сутки :D", reply_markup=markup)
    conn.commit()
    cur.close()
    conn.close()


@bot.message_handler(content_types=['text'])
def check(message):
    global status, mode, current_id, value
    if message.text == 'control':
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()
        cur.execute(f'SELECT status FROM users WHERE tg_id = {message.chat.id}')
        status = cur.fetchone()[0]
        if status != "Админ":
            bot.send_message(message.chat.id, 'Введите пароль для управления админ-панелью:')
            status = 'check'
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton(text='Выдать валюту', callback_data='drop')
            btn2 = types.InlineKeyboardButton(text='Забрать валюту', callback_data='take')
            markup.add(btn1, btn2)
            bot.send_message(chat_id=message.chat.id, text='Добро пожаловать, админ!', reply_markup=markup)
            status = ''
            cur.close()
            conn.close()
    elif status == 'check':
        if message.text == 'lRuNVIaJd4Dfd1698klVt4x':

            conn = sqlite3.connect('users.sql')
            cur = conn.cursor()
            cur.execute(f'UPDATE users '
                        f'SET status = "Админ" '
                        f'WHERE tg_id = {message.chat.id};')
            conn.commit()
            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton(text='Выдать валюту', callback_data='drop')
            btn2 = types.InlineKeyboardButton(text='Забрать валюту', callback_data='take')
            markup.add(btn1, btn2)
            bot.send_message(chat_id=message.chat.id, text='Добро пожаловать, админ!', reply_markup=markup)
            status = ''
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
            markup.add(btn)
            bot.send_message(chat_id=message.chat.id, text='Неверный пароль!', reply_markup=markup)
    else:
        if mode == 'take_last':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
            markup.add(btn)
            if message.text.isdigit():
                if current_id:

                    conn = sqlite3.connect('users.sql')
                    cur = conn.cursor()
                    try:
                        if value == 'balance':
                            cur.execute(f'UPDATE users '
                                        f'SET balance = balance - {message.text} '
                                        f'WHERE tg_id = {current_id};')
                            bot.send_message(chat_id=message.chat.id,
                                             text=f'✅Вы успешно изъяли со счета пользователя {current_id} {message.text}🗝',
                                             reply_markup=markup)
                        elif value == 'diamonds':
                            cur.execute(f'UPDATE users '
                                        f'SET diamonds = diamonds - {message.text} '
                                        f'WHERE tg_id = {current_id};')
                            bot.send_message(chat_id=message.chat.id,
                                             text=f'✅Вы успешно изъяли со счета пользователя {current_id} {message.text}💎',
                                             reply_markup=markup)
                        conn.commit()
                        cur.close()
                        conn.close()
                    except TypeError:
                        bot.send_message(chat_id=message.chat.id,
                                         text='Ошибка. Повторите попытку.', reply_markup=markup)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Ошибка при вводе суммы!', reply_markup=markup)

        elif mode == 'drop_last':
            if message.text.isdigit():
                if current_id:
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    btn = types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
                    markup.add(btn)
                    conn = sqlite3.connect('users.sql')
                    cur = conn.cursor()
                    try:
                        if value == 'balance':
                            cur.execute(f'UPDATE users '
                                        f'SET balance = balance + {message.text} '
                                        f'WHERE tg_id = {current_id};')
                            bot.send_message(chat_id=message.chat.id,
                                             text=f'✅Вы успешно пополнили счет пользователя {current_id} на {message.text}🗝',
                                             reply_markup=markup)
                        elif value == 'diamonds':
                            cur.execute(f'UPDATE users '
                                        f'SET diamonds = diamonds + {message.text} '
                                        f'WHERE tg_id = {current_id};')
                            bot.send_message(chat_id=message.chat.id,
                                             text=f'✅Вы успешно пополнили счет пользователя {current_id} на {message.text}💎',
                                             reply_markup=markup)

                        conn.commit()
                        cur.close()
                        conn.close()
                    except TypeError:
                        bot.send_message(chat_id=message.chat.id,
                                         text='Ошибка. Повторите попытку.', reply_markup=markup)
        elif mode == 'take_next':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup.add(btn)
            if message.text.isdigit():
                conn = sqlite3.connect('users.sql')
                cur = conn.cursor()
                try:
                    cur.execute(f'SELECT tg_id FROM users WHERE tg_id = {message.text}')
                    current_id = cur.fetchone()[0]
                    if current_id:
                        mode = 'take_last'
                        bot.send_message(chat_id=message.chat.id,
                                         text='Введите количество валюты для изъятия:', reply_markup=markup)
                    else:
                        bot.send_message(chat_id=message.chat.id,
                                         text='Данный пользователь не состоит в базе данных', reply_markup=markup)
                    cur.close()
                    conn.close()
                except TypeError:
                    bot.send_message(chat_id=message.chat.id,
                                     text='Данный пользователь не состоит в базе данных', reply_markup=markup)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Данный пользователь не состоит в базе данных', reply_markup=markup)

        elif mode == 'drop_next':
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup.add(btn)
            if message.text.isdigit():
                conn = sqlite3.connect('users.sql')
                cur = conn.cursor()
                try:
                    cur.execute(f'SELECT tg_id FROM users WHERE tg_id = {message.text}')
                    current_id = cur.fetchone()[0]

                    if current_id:
                        mode = 'drop_last'
                        bot.send_message(chat_id=message.chat.id,
                                         text='Введите количество валюты для выдачи:', reply_markup=markup)
                    else:
                        bot.send_message(chat_id=message.chat.id,
                                         text='Данный пользователь не состоит в базе данных', reply_markup=markup)
                    cur.close()
                    conn.close()
                except TypeError:
                    bot.send_message(chat_id=message.chat.id,
                                     text='Данный пользователь не состоит в базе данных', reply_markup=markup)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='Данный пользователь не состоит в базе данных', reply_markup=markup)
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn = types.InlineKeyboardButton(text='Назад', callback_data='main_menu')
            markup.add(btn)
            bot.send_message(chat_id=message.chat.id,
                             text='Простите, но я отвечаю только на команды', reply_markup=markup)


bot.infinity_polling()
