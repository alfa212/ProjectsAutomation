import datetime as dt
from pprint import pprint

import telebot
from environs import Env
from django.core.management.base import BaseCommand

from automation.models import Manager, Student


def make_periods():
    time_from_available = []

    periods_string = ''

    time_num = 1

    for manager in Manager.objects.all():
        if manager.time_from and manager.time_to:
            time_from = dt.datetime.strptime(str(manager.time_from), '%H:%M:%S')
            time_to = dt.datetime.strptime(str(manager.time_to), '%H:%M:%S')
            
            periods = (time_to - time_from).seconds // 60 // 30

            for _ in range(0, periods):
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

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id,
                         f'Пожалуйста, выберите подходящее вам время занятий (ответьте цифрой):\n'
                         f'{time_periods[1]}'
                         )

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text in [str(i) for i in range(1, len(time_periods[0])+1)]:
            tg_username = f'@{message.from_user.username}'
            time = time_periods[0][int(message.text) - 1]

            try:
                student = Student.objects.get(tg_username=tg_username)
                student.time = time
                student.save()
            except Student.DoesNotExist:
                bot.send_message(
                    message.chat.id,
                    'Сожалеем, вас нет в списках.'
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Спасибо!\nМы постараемся учесть ваше пожелание!'
                )
        else:
            bot.send_message(
                message.chat.id,
                'Вы прислали не ту цифру'
            )

    bot.polling(none_stop=True, interval=0)


class Command(BaseCommand):
    help = 'Run the telegram bot'

    def handle(self, *args, **kwargs):
        env = Env()
        env.read_env()

        token = env('BOT_TOKEN')
        telegram_bot(token, make_periods())
