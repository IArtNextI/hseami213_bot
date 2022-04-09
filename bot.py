import datetime
import logging
import re
import requests
import ruz
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types

import config
import key
import admin
from commands_config import bot_command
from messages_config import bot_message


bot = telebot.TeleBot(key.TOKEN, parse_mode=None)

last_query = dict()
last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
todays_schedule = ruz.person_lessons(email=config.email, from_date=last_update_date, to_date=last_update_date)
queries_without_cleanup = 0

CORRECT_IDS = admin.CORRECT_IDS.copy()
ADMIN_IDS = admin.ADMIN_IDS.copy()

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hseami213_bot')

scheduler = BackgroundScheduler(timezone=config.timezone)


def update_today_schedule():
    global last_update_date, todays_schedule
    last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
    todays_schedule = ruz.person_lessons(email=config.email, from_date=datetime.datetime.today().strftime('%Y.%m.%d'),
                                         to_date=datetime.datetime.today().strftime('%Y.%m.%d'))


def get_command_name(message):
    return message.text.replace("@hseami213_bot", '').split()[0][1:]


def check_IDS(message):
    return not CORRECT_IDS or message.chat.id in CORRECT_IDS or message.from_user.id in ADMIN_IDS


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
    if not check_IDS(message):
        return
    bot.reply_to(message, bot_message[bot_command.help])


@bot.message_handler(commands=[bot_command.add])
def add_deadline(message):
    global last_query, CORRECT_IDS
    cleanup()
    chat_id = message.chat.id
    if not check_IDS(message):
        return
    user = message.from_user.id
    current = last_query.get(user, None)
    last_query[user] = (datetime.datetime.now(), 1)
    bot.reply_to(message, "Название дисциплины?")


def get_active_deadlines():
    list_of_active_dealines = []
    with open(config.log_path, 'r') as fin:
        lines = fin.readlines()
    logger.info('Active deadlines:')
    for line in lines:
        try:
            tad = line.strip().split(';')[0]
            datte = list(map(int, tad.split()[0].split('.')))
            timme = list(map(int, tad.split()[1].split(':')))
            #        print(datetime.datetime.now(tz=config.timezone) + datetime.timedelta(minutes=30))
            #        print(datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59, tzinfo=config.timezone))
            if datetime.datetime.now(tz=config.timezone) + datetime.timedelta(minutes=30) < datetime.datetime(datte[2],
                                                                                                              datte[1],
                                                                                                              datte[0],
                                                                                                              timme[0],
                                                                                                              timme[1],
                                                                                                              59,
                                                                                                              tzinfo=config.timezone):
                # This line satisfies the condition, parse it
                splitted = line.strip().split(';')
                logger.info(splitted)
                list_of_active_dealines.append([ datetime.datetime(datte[2], datte[1], datte[0], timme[0], timme[1], 59,
                                                                  tzinfo=config.timezone), *splitted])
        except Exception as e:
            logger.error(e)
    return list_of_active_dealines


@bot.message_handler(commands=[bot_command.get])
def get_deadlines(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return
    list_of_active_deadlines = get_active_deadlines()
    if list_of_active_deadlines:
        list_of_active_deadlines.sort(key=lambda x: x[0])
        deadlines_message = 'Список ближайших дедлайнов:\n\n'

        for date, *splitted in list_of_active_deadlines:
            res = splitted[0] + ' --- '
            if splitted[2]:
                res += '<a href=\"' + splitted[2] + '\">' + splitted[1] + "</a>\n"
            else:
                res += splitted[1] + '\n'
            deadlines_message += res

        bot.reply_to(message, deadlines_message, parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Я честно не думал, что это когда-нибудь отработает, но дедлайнов нет...")


@bot.message_handler(commands=[bot_command.delete])
def delete_message(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return
    with open(config.log_path, 'r') as fin:
        lines = fin.readlines()
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
    if not check_IDS(message):
        return
    bot.reply_to(message, bot_message[get_command_name(message)](message))


@bot.message_handler(commands=[bot_command.wiki, bot_command.marks, bot_command.linal, bot_command.recordings])
def send_md2(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return
    res = bot_message[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="MarkdownV2", disable_web_page_preview=True)


@bot.message_handler(commands=[bot_command.mark_formulas])
def send_md(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return
    res = bot_message[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=[bot_command.today])
def send_todays_schedule(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return

    if last_update_date < datetime.datetime.today().strftime('%Y.%m.%d'):
        update_today_schedule()
    if len(todays_schedule) == 0:
        bot.reply_to(message, 'Нет у тебя сегодня пар, дурень. Иди отдохни...', parse_mode="Markdown",
                     disable_web_page_preview=True)
        return
    res = bot_message[bot_command.today](todays_schedule)
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=[bot_command.oakbus, 'bus', 'avtobus', 'oakpass', 'avtozak', 'partyvan', 'boynextbus'])
def send_bus_schedule(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return

    res = bot_message[bot_command.oakbus]
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=['addid'])
def add_ID(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        candidate_id = int(message.text.split()[1])
        CORRECT_IDS.append(candidate_id)
        with open(config.ids_path, 'w+') as fout:
            print(candidate_id, file=fout)
        bot.reply_to(message, "Done")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['readids', 'printids', 'getids'])
def read_ID(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        result = ''
        for index, line in enumerate(CORRECT_IDS):
            result += "--> " + str(line) + '\n'
        bot.reply_to(message, result)
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['delid'])
def delete_ID(message):
    global CORRECT_IDS
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        current_id = int(message.text.split()[1])
        found_id = False
        fin = open(config.ids_path, 'r')
        lines = fin.readlines()
        fin.close()
        fout = open(config.ids_path, 'w')
        CORRECT_IDS = admin.CORRECT_IDS.copy()
        for line in lines:
            if int(line) == current_id:
                found_id = True
                continue
            CORRECT_IDS.append(int(line))
            print(line, file=fout, end='')
        fout.close()
        bot.reply_to(message, "Done" if found_id else "Did not find such entry")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['register'])
def register_chat(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        candidate_id = message.chat.id
        CORRECT_IDS.append(candidate_id)
        with open(config.ids_path, 'w+') as fout:
            print(candidate_id, file=fout)
        bot.reply_to(message, "Done")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['resetids'])
def reset_IDS(message):
    global ADMIN_IDS, CORRECT_IDS
    if message.from_user.id not in ADMIN_IDS:
        return
    ADMIN_IDS = admin.ADMIN_IDS.copy()
    CORRECT_IDS = admin.CORRECT_IDS.copy()
    with open(config.ids_path, 'w'):
        pass
    bot.reply_to(message, "Done")


def add_reminder(name, deadline, chat_id):
    logger.debug('sending reminder!')
    text = f'Дедлайн по {name} : {deadline}'
    bot.send_message(chat_id, text)


@bot.message_handler(commands=['levo'])
def marks(message):
    global last_query, CORRECT_IDS
    cleanup()
    if not check_IDS(message):
        return
    res = """<a href="https://t.me/c/1567266992/88">Ответы</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)


# @bot.message_handler(func=lambda x: x.text[:4] == '/add' and len(x.text) > 4)
@bot.message_handler(
    func=lambda x: True and get_command_name(x) not in [bot_command.add, bot_command.get, bot_command.chatid,
                                                        bot_command.delete])
def process(message):
    try:
        cleanup()
        chat_id = message.chat.id
        if not check_IDS(message):
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
                                         tzinfo=config.timezone)
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
            elif ans.lower() in ["сори, нет("]:
                bot.reply_to(message, "(O.o)? Записано... \\(0-0)/")
            elif '.' in ans:
                new_entry += message.text.strip()
                bot.reply_to(message, "Записано \\(0-0)/")
            else:
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
                return

            with open(config.log_path, 'a') as fout:
                fout.write(new_entry + '\n')

            scheduler.add_job(add_reminder, 'date',
                              run_date=current[-1] - datetime.timedelta(hours=1) - datetime.timedelta(minutes=30),
                              args=[current[-2], current[3], chat_id])
            for job in scheduler.get_jobs():
                logger.debug('My: ' + str(job.trigger))
        elif current[1] == -1:
            index = int(message.text.strip())
            with open(config.log_path, 'r') as fin:
                lines = fin.readlines()
            if index >= len(lines):
                bot.reply_to(message, "Sorry it seems it a DDOS attack")
            else:
                with open(config.log_path, 'w') as fout:
                    for i in range(len(lines)):
                        if i == index:
                            continue
                        fout.write(lines[i])
                last_query[user] = (datetime.datetime.now(), 0)
                bot.reply_to(message, "Уничтожил, низвел до атомов...")
    except Exception as e:
        logger.error(e)
        bot.reply_to(message, "Sorry it seems it a DDOS attack")


def process_deadlines():
    list_of_active_deadlines = get_active_deadlines()
    for date, *splitted in list_of_active_deadlines:
        scheduler.add_job(add_reminder, 'date',
                          run_date=max(date - datetime.timedelta(hours=1) - datetime.timedelta(minutes=30),
                                       datetime.datetime.now(tz=config.timezone)
                                       ),
                          args=[splitted[0], splitted[1], -1001597210278])


def load_IDS():
    with open(config.ids_path, 'r') as fin:
        lines = fin.readlines()
        for line in lines:
            c = line.replace('\n', '')
            current_id = int(c)
            CORRECT_IDS.append(current_id)


def setup(debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    logger.info("hseami213_bot")
    scheduler.start()
    process_deadlines()
    load_IDS()


if __name__ == "__main__":
    setup(debug=True)
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.error(e)
