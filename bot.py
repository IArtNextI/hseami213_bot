import asyncio
import datetime
import key
import logging
import os
import pytz
import re
import requests
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

bot = telebot.TeleBot(key.TOKEN, parse_mode=None)

last_query = dict()
queries_without_cleanup = 0

CORRECT_IDS = []
timezone = pytz.timezone('Europe/Moscow')

path = "./log.txt"

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hseami213_bot')
logger.setLevel(logging.DEBUG)

scheduler = BackgroundScheduler(timezone=timezone)


def cleanup():
    global queries_without_cleanup, last_query
    queries_without_cleanup += 1
    if queries_without_cleanup >= 100:
        queries_without_cleanup = 0
        newdict = dict()
        for (k, v) in last_query.items():
            if (datetime.datetime.now() - v[0]).total_seconds() > 180:
                pass
            else:
                newdict[k] = v
        last_query = newdict


def add_reminders(task, deadline, chat_id):
    text = f'!!!Дедлайн по {task} : {deadline}'
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['add'])
def add_deadline(message):
    global last_query, CORRECT_IDS
    cleanup()
    chat_id = message.chat.id
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    user = message.from_user.id
    current = last_query.get(user, None)
    last_query[user] = (datetime.datetime.now(), 1)
    bot.reply_to(message, "Название дисциплины?")


@bot.message_handler(commands=['get'])
def get_deadlines(message):
    global last_query, CORRECT_IDS
    cleanup()
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    list_of_active_deadlines = []
    fin = open(path, 'r')
    lines = fin.readlines()
    fin.close()
    for line in lines:
        try:
            tad = line.strip().split(';')[0]
            datte = list(map(int, tad.split()[0].split('.')))
            timme = list(map(int, tad.split()[1].split(':')))
            #        print(datetime.datetime.now(tz=timezone) + datetime.timedelta(minutes=30))
            #        print(datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=timezone))
            if datetime.datetime.now(tz=timezone) + datetime.timedelta(minutes=30) < datetime.datetime(datte[2],
                                                                                                       datte[1],
                                                                                                       datte[0],
                                                                                                       timme[0],
                                                                                                       timme[1], 59,
                                                                                                       tzinfo=timezone):
                # This line satisfies the condition, parse it
                splitted = line.strip().split(';')
                res = splitted[0] + ' --- '
                if splitted[2]:
                    res += '<a href=\"' + splitted[2] + '\">' + splitted[1] + "</a>\n"
                else:
                    res += splitted[1] + '\n'
                print(res)
                list_of_active_deadlines.append(
                    [res, datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=timezone)])
        except:
            pass
    if list_of_active_deadlines:
        list_of_active_deadlines.sort(key=lambda x: x[1])
        bot.reply_to(message, 'Список ближайших дедлайнов:\n\n' + ''.join([x[0] for x in list_of_active_deadlines]),
                     parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Я честно не думал, что это когда-нибудь отработает, но дедлайнов нет...")


@bot.message_handler(commands=['userid'])
def get_chatid(message):
    global last_query, CORRECT_IDS
    cleanup()
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    bot.reply_to(message, str(message.from_user.id))


@bot.message_handler(commands=['chatid'])
def get_chatid(message):
    global last_query, CORRECT_IDS
    cleanup()
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    bot.reply_to(message, str(message.chat.id))


@bot.message_handler(commands=['delete'])
def delete_message(message):
    global last_query, CORRECT_IDS
    cleanup()
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    with open(path, 'r') as fin:
        lines = fin.readlines()
    res = 'Выберите, какую запись удалить:\n\n'
    for i in range(max(len(lines) - 15, 0), len(lines)):
        res += str(i) + " :: " + lines[i]
    bot.reply_to(message, res, disable_web_page_preview=True)
    user = message.from_user.id
    last_query[user] = (datetime.datetime.now(), -1)


# @bot.message_handler(func=lambda x: x.text[:4] == '/add' and len(x.text) > 4)
@bot.message_handler(
    func=lambda x: True and x.text.replace("@hseami213_bot", '').split()[0] not in ['/add', '/get', '/chatid',
                                                                                    '/delete'])
def process(message):
    try:
        cleanup()
        chat_id = message.chat.id
        if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
            return
        user = message.from_user.id
        current = last_query.get(user, None)
        deadline = datetime.datetime.now()
        name = ''
        if current is None or (datetime.datetime.now() - current[0]).total_seconds() > 180:
            return
        if current[1] == 1:
            name = message.text.strip()
            last_query[user] = (datetime.datetime.now(), 2, name)
            bot.reply_to(message, "Дедлайн? (dd.mm.yyyy hh:mm)")
        elif current[1] == 2:
            msg = message.text.strip()
            date, time = msg.split()
            deadline = datetime.datetime(*map(int, date.split('.')[::-1]), *map(int, time.split(':')), 59,
                                         tzinfo=timezone)
            last_query[user] = (datetime.datetime.now(), 3, current[2], msg, current[-1], deadline)
            bot.reply_to(message, "Ссылочку бы...")
        elif current[1] == 3:
            ans = message.text.strip()
            new_entry = current[3] + ';' + current[2] + ';'
            last_query[user] = (datetime.datetime.now(), 0)

            if ans.lower() in ['no', 'нет', 'не', 'неа', 'не-а', '-']:
                bot.reply_to(message, "И как людям жить? Ладно, записано \\(0-0)/")
            elif ans.lower() in ["не)"]:
                bot.reply_to(message, "-_- Это матан что ли? Ладно, записано \\(0-0)/")
            elif ans.lower() in ["Сори, нет("]:
                bot.reply_to(message, "(O.o)? Записано... \\(0-0)/")
            elif '.' in ans:
                new_entry += message.text.strip()
                bot.reply_to(message, "Записано \\(0-0)/")
            else:
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
                return

            with open(path, 'a') as fout:
                fout.write(new_entry + '\n')

            scheduler.add_job(add_reminders, 'date', run_date=current[-1] - datetime.timedelta(hours=1),
                              args=[current[-2], current[-1], chat_id])
        elif current[1] == -1:
            index = int(message.text.strip())
            with open(path, 'r') as fin:
                lines = fin.readlines()
            if index >= len(lines):
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
            else:
                with open(path, 'w') as fout:
                    for i in range(len(lines)):
                        if i == index:
                            continue
                        print(lines[i], file=fout)
                last_query[user] = (datetime.datetime.now(), 0)
                bot.reply_to(message, "Уничтожил, низвел до атомов...")
        else:
            bot.reply_to(message, "Sorry it seems it a DDOS attack")
    except Exception as e:
        bot.reply_to(message, "Sorry it seems it a DDOS attack")
        logger.error("Something went wrong:\n" + str(e) + '\n')


if __name__ == "__main__":
    logger.info("Starting hseami213_bot")
    scheduler.start()
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.error("Something went wrong:\n" + str(e) + '\n')
