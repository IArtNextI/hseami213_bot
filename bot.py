import telebot
from telebot import types
import requests
import re
import pytz
import datetime
import key

bot = telebot.TeleBot(key.TOKEN, parse_mode=None)

last_query = dict()
queries_without_cleanup = 0

CORRECT_IDS = []
timezone = pytz.timezone('Europe/Moscow')


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


@bot.message_handler(commands=['add'])
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


path = "hseami213_bot/log.txt"


@bot.message_handler(commands=['get'])
def get_deadlines(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
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


@bot.message_handler(commands=['userid'])
def get_chatid(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    bot.reply_to(message, str(message.from_user.id))




@bot.message_handler(commands=['chatid'])
def get_chatid(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    bot.reply_to(message, str(message.chat.id))


@bot.message_handler(commands=['delete'])
def delete_message(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    fin = open(path, 'r')
    lines = fin.readlines()
    fin.close()
    res = 'Выберите, какую запись удалить:\n\n'
    for i in range(max(len(lines) - 15, 0), len(lines)):
        res += str(i) + " :: " + lines[i]
    bot.reply_to(message, res, disable_web_page_preview=True)
    user = message.from_user.id
    last_query[user] = (datetime.datetime.now(), -1)


@bot.message_handler(commands=['wiki'])
def wiki(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = """<a href="http://wiki.cs.hse.ru/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0">Wiki</a>
<a href="http://wiki.cs.hse.ru/%D0%9B%D0%B8%D0%BD%D0%B5%D0%B9%D0%BD%D0%B0%D1%8F_%D0%B0%D0%BB%D0%B3%D0%B5%D0%B1%D1%80%D0%B0_%D0%B8_%D0%B3%D0%B5%D0%BE%D0%BC%D0%B5%D1%82%D1%80%D0%B8%D1%8F_%D0%BD%D0%B0_%D0%9F%D0%9C%D0%98_2021/2022_(%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA)">Линал</a>
<a href="http://wiki.cs.hse.ru/%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7_1_2021/2022_(%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA)">Матан</a>
<a href="http://wiki.cs.hse.ru/DM1-2021-22">Дискра</a>
<a href="http://wiki.cs.hse.ru/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D1%8B_%D0%B8_%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D1%8B_%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85_%D0%BF%D0%B8%D0%BB%D0%BE%D1%82%D0%BD%D1%8B%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA_2021/2022">Алгосы</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(commands=['marks'])
def marks(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = """<a href="https://docs.google.com/spreadsheets/d/1Uoe6ThMa5R8Qij3xexE1reel5aDLue47iFVm6xous_w/edit#gid=0">Линал Семы</a>
<a href="https://docs.google.com/spreadsheets/d/1HBbgUG6nstuJVWAXn7uoGD7tZ2uQesK27YXKN04ZsrE/edit#gid=1697515667">Линал ИДЗ</a>
<a href="https://docs.google.com/spreadsheets/d/1lkssP6PGxxfe15ffiPatcamoV9e-WOlq8ysUqIbuzTI/edit#gid=1488201705">Матан</a>
<a href="https://docs.google.com/spreadsheets/d/1kqDZ8_nL5rmzIAfL6nqkUpY8knbVtwFZrsq9gp3jabM/edit">Дискра</a>
<a href="https://docs.google.com/spreadsheets/d/1bRg_nUNZxfPY-JxFXvzAvPb-GwWZ8Cv8gxJSJgo-uhA/edit">Алгосы</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(commands=['mark_formulas'])
def marks(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = """*Линал*
Oитоговая = min(10; 0,32 · Oэкз + 0,23 · Oколл + 0,17 · Oк/р + 0,2 · Oд/з + 0,1 · Oсем + 0,08 · Oл)

*Матан*
О = 0.3 · (Кр1+Кр2) + 0.15 · (Кл1+Кл2) + 0.1 · Дз

*Дискра*
О = 0.3 · Околл + 0.15 · Оп/экз + 0.3 · Ои/экз + 0.25 · Одз

*Алгосы*
Оитог = 0.3 · Оконтесты (2 + 3 модуль) + 0.25 · Oлистки (2 + 3 модуль) + 0.15 · Oконтрольная + 0.3 · Oэкзамен + Oбонус

Оконтесты = 10 · ((КК + ДК)/ (ОЗ - поправка) + БЗ / ОЗ), где:

КК — баллы за короткие контесты
ДК — баллы за длинные контесты (исключая бонусные задачи)
БЗ — баллы за бонусные задачи в длинных контестах
ОЗ — общее число задач во всех контестах (исключая бонусные задачи)
Поправка по умолчанию равна нулю и может быть увеличена индивидуально для каждого студента при наличии пропусков по уважительным причинам."""
    bot.reply_to(message, res, parse_mode="MARKDOWN", disable_web_page_preview=True)



@bot.message_handler(commands=['linal'])
def marks(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message.chat.id):
        return
    res = """<a href="https://disk.yandex.ru/d/idvfp8FiufvVLA">Линал ДЗ</a>
<a href="https://disk.yandex.ru/i/ayIeELGipfO4_Q">Линал Кострикин</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)



# @bot.message_handler(func=lambda x: x.text[:4] == '/add' and len(x.text) > 4)
@bot.message_handler(func=lambda x: True and x.text.replace("@hseami213_bot", '').split()[0] not in ['/add', '/get', '/chatid', '/delete'])
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
        elif current[1] == -1:
            index = int(message.text.strip())
            fin = open(path, 'r')
            lines = fin.readlines()
            fin.close()
            if index >= len(lines):
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
            else:
                fout = open(path, 'w')
                for i in range(len(lines)):
                    if i == index:
                        continue
                    print(lines[i], file=fout, end='')
                fout.close()
                last_query[user] = (datetime.datetime.now(), 0)
                bot.reply_to(message, "Уничтожил, низвел до атомов...")
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