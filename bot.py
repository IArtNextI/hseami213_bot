import telebot
from telebot import types
import requests
import re
import pytz
import datetime

bot = telebot.TeleBot("", parse_mode=None)

last_query = dict()
queries_without_cleanup = 0

CORRECT_IDS = []
timezone = pytz.timezone('Europe/Moscow')


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


path = "hseami213_bot/log.txt"


@bot.message_handler(commands=['get'])
def get_deadlines(message):
    global last_query, CORRECT_IDS
    cleanup()
    if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
        return
    list_of_active_dealines = []
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
            if datetime.datetime.now(tz=timezone) + datetime.timedelta(minutes=30) < datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=timezone):
                # This line satisfies the condition, parse it
                splitted = line.strip().split(';')
                res = splitted[0] + ' --- '
                if splitted[2]:
                    res += '<a href=\"' + splitted[2] + '\">' + splitted[1] + "</a>\n"
                else:
                    res += splitted[1] + '\n'
                print(res)
                list_of_active_dealines.append([res, datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=timezone)])
        except:
            pass
    if list_of_active_dealines:
        list_of_active_dealines.sort(key=lambda x:x[1])
        bot.reply_to(message, 'Список ближайших дедлайнов:\n\n' + ''.join([x[0] for x in list_of_active_dealines]),
                     parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Я честно не думал, что это когда-нибудь отработает, но дедлайнов нет...")


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
    bot.reply_to(message, str(message.chat.id))


# @bot.message_handler(func=lambda x: x.text[:4] == '/add' and len(x.text) > 4)
@bot.message_handler(func=lambda x: True and x.text.replace("@hseami213_bot", '').split()[0] not in ['/add', '/get', '/chatid', '/delete'])
def process(message):
    try:
        cleanup()
        chat_id = message.chat.id
        if CORRECT_IDS and message.chat.id not in CORRECT_IDS:
            return
        user = message.from_user.id
        current = last_query.get(user, None)
        if current is None or (datetime.datetime.now() - current[0]).total_seconds() > 180:
            return
        if current[1] == 1:
            name = message.text.strip()
            last_query[user] = (datetime.datetime.now(), 2, name)
            bot.reply_to(message, "Дедлайн? (dd.mm.yyyy hh:mm)")
        elif current[1] == 2:
            last_query[user] = (datetime.datetime.now(), 3, current[2], message.text.strip())
            bot.reply_to(message, "Ссылочку бы...")
        elif current[1] == 3:
            ans = message.text.strip()
            if ans.lower() in ['no', 'нет', 'не', 'неа', 'не-а', '-']:
                fout = open(path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "И как людям жить? Ладно, записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif ans.lower() in ["не)"]:
                fout = open(path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "-_- Это матан что ли? Ладно, записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif ans.lower() in ["Сори, нет("]:
                fout = open(path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "(O.o)? Записано... \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif '.' in ans:
                fout = open(path, 'a')
                print(current[3] + ';' + current[2] + ';' + message.text.strip(), file=fout)
                fout.close()
                bot.reply_to(message, "Записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            else:
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
        else:
            bot.reply_to(message, "Sorry it seems it a DDOS attack")
    except:
        bot.reply_to(message, "Sorry it seems it a DDOS attack")


if __name__ == "__main__":
    print("hseami213_bot")
    while True:
        try:
            bot.polling()
        except:
            pass