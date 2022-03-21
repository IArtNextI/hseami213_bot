import datetime
import re

import requests
import ruz
import telebot
from telebot import types

import config
import key
from commands_config import bot_command
from messages_config import bot_message

bot = telebot.TeleBot(key.TOKEN, parse_mode=None)

last_query = dict()
last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
todays_schedule = ruz.person_lessons(email = config.email, from_date=last_update_date, to_date=last_update_date)
queries_without_cleanup = 0

CORRECT_IDS = []

def update_today_schedule():
    global last_update_date, todays_schedule
    last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
    todays_schedule = ruz.person_lessons(email = config.email, from_date=datetime.datetime.today().strftime('%Y.%m.%d'), to_date=datetime.datetime.today().strftime('%Y.%m.%d'))

def get_command_name(message):
    return message.text.replace("@hseami213_bot", '').split()[0][1:]

def check_IDS(chatid):
    return not CORRECT_IDS or chatid in CORRECT_IDS


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


@bot.message_handler(commands=[bot_command.start, bot_command.help])
def add_deadline(message):
    global last_query, CORRECT_IDS
    cleanup()
    chat_id = message.chat.id
    if not check_IDS(chat_id):
        return
    bot.reply_to(message, bot_message[bot_command.help])


@bot.message_handler(commands=[bot_command.add])
def add_deadline(message):
    global last_query, CORRECT_IDS
    cleanup()
    chat_id = message.chat.id
    if not check_IDS(chat_id):
        return
    user = message.from_user.id
    current = last_query.get(user, None)
    last_query[user] = (datetime.datetime.now(), 1)
    bot.reply_to(message, "Название дисциплины?")

@bot.message_handler(commands=[bot_command.get])
def get_deadlines(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    list_of_active_dealines = []
    fin = open(config.log_path, 'r')
    lines = fin.readlines()
    fin.close()
    for line in lines:
        try:
            tad = line.strip().split(';')[0]
            datte = list(map(int, tad.split()[0].split('.')))
            timme = list(map(int, tad.split()[1].split(':')))
    #        print(datetime.datetime.now(tz=config.timezone) + datetime.timedelta(minutes=30))
    #        print(datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=config.timezone))
            if datetime.datetime.now(tz=config.timezone) + datetime.timedelta(minutes=30) < datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=config.timezone):
                # This line satisfies the condition, parse it
                splitted = line.strip().split(';')
                res = splitted[0] + ' --- '
                if splitted[2]:
                    res += '<a href=\"' + splitted[2] + '\">' + splitted[1] + "</a>\n"
                else:
                    res += splitted[1] + '\n'
                print(res)
                list_of_active_dealines.append([res, datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=config.timezone)])
        except:
            pass
    if list_of_active_dealines:
        list_of_active_dealines.sort(key=lambda x:x[1])
        bot.reply_to(message, 'Список ближайших дедлайнов:\n\n' + ''.join([x[0] for x in list_of_active_dealines]),
                     parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Я честно не думал, что это когда-нибудь отработает, но дедлайнов нет...")

@bot.message_handler(commands=[bot_command.delete])
def delete_message(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    fin = open(config.log_path, 'r')
    lines = fin.readlines()
    fin.close()
    res = 'Выберите, какую запись удалить:\n\n'
    for i in range(max(len(lines) - 15, 0), len(lines)):
        res += str(i) + " :: " + lines[i]
    bot.reply_to(message, res, disable_web_page_preview=True)
    user = message.from_user.id
    last_query[user] = (datetime.datetime.now(), -1)

@bot.message_handler(commands=[bot_command.userid, bot_command.chatid])
def get_info(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    bot.reply_to(message, bot_message[get_command_name(message)](message))

@bot.message_handler(commands=[bot_command.wiki, bot_command.marks, bot_command.linal])
def send_md2(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = bot_message[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="MarkdownV2", disable_web_page_preview=True)

@bot.message_handler(commands=[bot_command.mark_formulas])
def send_md(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = bot_message[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(commands=[bot_command.today])
def send_todays_schedule(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return

    if last_update_date < datetime.datetime.today().strftime('%Y.%m.%d'):
        update_today_schedule()
    if len(todays_schedule) == 0:
        bot.reply_to(message, 'Нет у тебя сегодня пар, дурень. Иди отдохни...', parse_mode="Markdown", disable_web_page_preview=True)
        return
    res = bot_message[bot_command.today](todays_schedule)
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)

# @bot.message_handler(func=lambda x: x.text[:4] == '/add' and len(x.text) > 4)
@bot.message_handler(func=lambda x: True and get_command_name(x) not in [bot_command.add, bot_command.get, bot_command.chatid, bot_command.delete])
def process(message):
    try:
        cleanup()
        chat_id = message.chat.id
        if not check_IDS(message.chat.id):
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
            tad = message.text.strip()
            datte = list(map(int, tad.split()[0].split('.')))
            timme = list(map(int, tad.split()[1].split(':')))
            last_query[user] = (datetime.datetime.now(), 3, current[2], message.text.strip())
            bot.reply_to(message, "Ссылочку бы...")
        elif current[1] == 3:
            ans = message.text.strip()
            if ans.lower() in ['no', 'нет', 'не', 'неа', 'не-а', '-']:
                fout = open(config.log_path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "И как людям жить? Ладно, записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif ans.lower() in ["не)"]:
                fout = open(config.log_path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "-_- Это матан что ли? Ладно, записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif ans.lower() in ["сори, нет("]:
                fout = open(config.log_path, 'a')
                print(current[3] + ';' + current[2] + ';', file=fout)
                fout.close()
                bot.reply_to(message, "(O.o)? Записано... \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            elif '.' in ans:
                fout = open(config.log_path, 'a')
                print(current[3] + ';' + current[2] + ';' + message.text.strip(), file=fout)
                fout.close()
                bot.reply_to(message, "Записано \\(0-0)/")
                last_query[user] = (datetime.datetime.now(), 0)
            else:
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
        elif current[1] == -1:
            index = int(message.text.strip())
            fin = open(config.log_path, 'r')
            lines = fin.readlines()
            fin.close()
            if index >= len(lines):
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
            else:
                fout = open(config.log_path, 'w')
                for i in range(len(lines)):
                    if i == index:
                        continue
                    print(lines[i], file=fout, end='')
                fout.close()
                last_query[user] = (datetime.datetime.now(), 0)
                bot.reply_to(message, "Уничтожил, низвел до атомов...")
    except:
        bot.reply_to(message, "Sorry it seems it a DDOS attack")


if __name__ == "__main__":
    print("hseami213_bot")
    while True:
        try:
            bot.polling()
        except:
            pass
