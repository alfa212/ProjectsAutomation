import os
import json
import datetime as dt
from pprint import pprint

from dotenv import load_dotenv
import telebot


def make_periods(managers):
    with open(managers, 'r', encoding='utf-8') as managers:
        managers = json.load(managers)

    time_from_available = []

    periods_string = ''

    time_num = 1

    for manager in managers:
        if manager['time_from'] and manager['time_to']:
            time_from = dt.datetime.strptime(manager['time_from'], '%H:%M')
            time_to = dt.datetime.strptime(manager['time_to'], '%H:%M')
            periods = (time_to - time_from).seconds // 60 // 30

            for period in range(0, periods):
                if time_from.time() not in time_from_available:
                    time_from_available.append(time_from.time())
                    periods_string += f'{time_num}) ' \
                                      f'{time_from.strftime("%H:%M")} - ' \
                                      f'{(time_from + dt.timedelta(minutes=30)).strftime("%H:%M")}\n'
                time_from += dt.timedelta(minutes=30)
                time_num += 1

    return [time_from_available, periods_string]


def telegram_bot(token, time_periods):
    bot = telebot.TeleBot(token)

    user_out = {}

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id,
                         f'Пожалуйста, выберите подходящее вам время занятий (ответьте цифрой):\n'
                         f'{time_periods[1]}'
                         )

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text in [str(i) for i in range(1, len(time_periods[0])+1)]:
            bot.send_message(message.chat.id,
                             f'Спасибо!\nМы постараемся учесть ваше пожелание!\n'
                             f'----------------\n'
                             f'Отладочная информация. В БД запишется:\n'
                             f'{message.from_user.username}\n'
                             f'{time_periods[0][int(message.text) - 1]}'
                             )
            user_out["tg_username"] = message.from_user.username
            user_out["time_from"] = time_periods[0][int(message.text) - 1]
            pprint(user_out)
        else:
            bot.send_message(
                message.chat.id,
                'Вы прислали не ту цифру'
            )

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    load_dotenv()

    token = os.getenv('BOT_TOKEN')
    file = 'managers.json'

    telegram_bot(token, make_periods(file))

