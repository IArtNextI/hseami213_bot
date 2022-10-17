from unicodedata import name
from pytz import timezone
import admin
import config
import key
import subscribe
from config_commands import BotCommand
from config_messages import BotMessage
from models import Deadline, DeadlineManager
from util import *

import csv
import datetime
import logging
import re
import ruz
import telebot
import time
from apscheduler.schedulers.background import BackgroundScheduler
from collections import namedtuple
from telebot import types


subscribers = subscribe.SubscriberHolder()
bot = telebot.TeleBot(key.TOKEN, parse_mode=None)

deadline_manager = DeadlineManager()

last_query = dict()
last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
todays_schedule = ruz.person_lessons(email=config.EMAIL, from_date=last_update_date, to_date=last_update_date)
queries_without_cleanup = 0

CORRECT_IDs = admin.CORRECT_IDs.copy()
ADMIN_IDs = admin.ADMIN_IDs.copy()

# logger
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hseami213_bot')

# scheduler
scheduler = BackgroundScheduler(timezone=config.TIMEZONE)


def update_today_schedule():
    global last_update_date, todays_schedule
    last_update_date = datetime.datetime.today().strftime('%Y.%m.%d')
    todays_schedule = ruz.person_lessons(email=config.email, from_date=datetime.datetime.today().strftime('%Y.%m.%d'),
                                         to_date=datetime.datetime.today().strftime('%Y.%m.%d'))


def get_command_name(message):
    return message.text.replace("@hseami213_bot", '').split()[0][1:]


def check_IDs(message):
    return not CORRECT_IDs or message.chat.id in CORRECT_IDs or message.from_user.id in ADMIN_IDs


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

@bot.message_handler(commands=[BotCommand.subscribe, BotCommand.unsubscribe])
def user_subscribe(message):
    global last_query, CORRECT_IDs, subscribers
    cleanup()
    chat_id = message.chat.id
    if not check_IDs(message):
        return

    if get_command_name(message) == BotCommand.subscribe:
        if len(message.text.split()) > 2:
            bot.reply_to(message, 'Чет ты фигню мне пишешь, не будет тебя в списке')
        elif len(message.text.split()) == 2 and len(message.text.split()[1]) > 1:
            bot.reply_to(message, 'Дай один смайл/символ, а то хз как тебя звать то')
        elif len(message.text.split()) == 2 and len(message.text.split()[1]) == 1:
            subscribers.subscribe(subscribe.Subscriber(message.from_user.id, message.from_user.username, message.text.split()[1]))
            bot.reply_to(message, BotMessage[BotCommand.subscribe])
        else:
            subscribers.subscribe(subscribe.Subscriber(message.from_user.id, message.from_user.username))
            bot.reply_to(message, BotMessage[BotCommand.subscribe])
    else:
        subscribers.unsubscribe(subscribe.Subscriber(message.from_user.id, message.from_user.username))
        bot.reply_to(message, BotMessage[BotCommand.unsubscribe])


@bot.message_handler(commands=[BotCommand.start, BotCommand.help])
def start(message):
    global last_query, CORRECT_IDs
    cleanup()
    chat_id = message.chat.id
    if not check_IDs(message):
        return
    bot.reply_to(message, BotMessage[BotCommand.help])

def get_active_deadlines(chat_id):
    try:
        with open(config.PATH_CHAT_DATA.format(chat_id), newline='', mode='r') as fin:
            reader = csv.reader(fin)
            next(reader)
            res = []
            for row in reader:
                row = [convert(value) for convert, value in zip(config.DEADLINE_FIELDS_TYPES, row)]
                res.append(Deadline(*row))
                if (res[-1].timestamp < time.time()):
                    res.pop()
            return res
    except FileNotFoundError:
        return []


@bot.message_handler(commands=[BotCommand.get])
def get_deadlines(message):
    cleanup()
    if not check_IDs(message):
        return
    list_of_active_deadlines = get_active_deadlines(message.chat.id)
    if list_of_active_deadlines:
        list_of_active_deadlines.sort(key=lambda x: x.timestamp)
        deadlines_message = 'Список ближайших дедлайнов:\n\n'

        for deadline in list_of_active_deadlines:
            formatted_date = timestamp_to_date(deadline.timestamp)
            res = formatted_date + ' --- '
            if deadline.url:
                res += f'<a href=\"{deadline.url}\"> {deadline.text} </a>\n'
            else:
                res += f'{deadline.text}\n'
            deadlines_message += res

        bot.reply_to(message, deadlines_message, parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(message, "Я честно не думал, что это когда-нибудь отработает, но дедлайнов нет...")


@bot.message_handler(commands=[BotCommand.delete])
def delete_message(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    with open(config.log_path, 'r') as fin:
        lines = fin.readlines()
    res = 'Выберите, какую запись удалить:\n\n'
    for i in range(max(len(lines) - 15, 0), len(lines)):
        res += str(i) + " :: " + lines[i]
    bot.reply_to(message, res, disable_web_page_preview=True)
    user = message.from_user.id
    last_query[user] = (datetime.datetime.now(), -1)


@bot.message_handler(commands=[BotCommand.userid, BotCommand.chatid])
def get_info(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    bot.reply_to(message, BotMessage[get_command_name(message)](message))


@bot.message_handler(commands=[BotCommand.wiki, BotCommand.marks, BotCommand.linal, BotCommand.recordings])
def send_md2(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    res = BotMessage[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="MarkdownV2", disable_web_page_preview=True)


@bot.message_handler(commands=[BotCommand.mark_formulas])
def send_md(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    res = BotMessage[get_command_name(message)]
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=[BotCommand.all, BotCommand.subs])
def slash_all(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return

    if get_command_name(message) == BotCommand.subs:
        res = '\n'.join(subscribers.get_subs_list())
    else:
        res = ''.join(subscribers.get_beautiful_links())
        
    bot.reply_to(message, res, parse_mode="MarkdownV2", disable_web_page_preview=True)


@bot.message_handler(commands=[BotCommand.today])
def send_todays_schedule(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return

    if last_update_date < datetime.datetime.today().strftime('%Y.%m.%d'):
        update_today_schedule()
    if len(todays_schedule) == 0:
        bot.reply_to(message, 'Нет у тебя сегодня пар, дурень. Иди отдохни...', parse_mode="Markdown",
                     disable_web_page_preview=True)
        return
    res = BotMessage[BotCommand.today](todays_schedule)
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=[BotCommand.oakbus] + config.BUS_COMMANDS)
def send_bus_schedule(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return

    res = BotMessage[BotCommand.oakbus]
    bot.reply_to(message, res, parse_mode="Markdown", disable_web_page_preview=True)


@bot.message_handler(commands=['addid'])
def add_ID(message):
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        candidate_id = int(message.text.split()[1])
        CORRECT_IDs.append(candidate_id)
        with open(config.PATH_IDS, 'w+') as fout:
            print(candidate_id, file=fout)
        bot.reply_to(message, "Done")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['readids', 'printids', 'getids'])
def read_ID(message):
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        result = ''
        for index, line in enumerate(CORRECT_IDs):
            result += "--> " + str(line) + '\n'
        bot.reply_to(message, result)
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['delid'])
def delete_ID(message):
    global CORRECT_IDs
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        current_id = int(message.text.split()[1])
        found_id = False
        fin = open(config.PATH_IDS, 'r')
        lines = fin.readlines()
        fin.close()
        fout = open(config.PATH_IDS, 'w')
        CORRECT_IDs = admin.CORRECT_IDs.copy()
        for line in lines:
            if int(line) == current_id:
                found_id = True
                continue
            CORRECT_IDs.append(int(line))
            print(line, file=fout, end='')
        fout.close()
        bot.reply_to(message, "Done" if found_id else "Did not find such entry")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['register'])
def register_chat(message):
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        candidate_id = message.chat.id
        CORRECT_IDs.append(candidate_id)
        with open(config.PATH_IDS, 'w+') as fout:
            print(candidate_id, file=fout)
        bot.reply_to(message, "Done")
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['resetids'])
def reset_IDs(message):
    global ADMIN_IDs, CORRECT_IDs
    if message.from_user.id not in ADMIN_IDs:
        return
    ADMIN_IDs = admin.ADMIN_IDs.copy()
    CORRECT_IDs = admin.CORRECT_IDs.copy()
    with open(config.PATH_IDS, 'w'):
        pass
    bot.reply_to(message, "Done")


def add_reminder(name, timestamp, chat_id):
    '''
    Function that sends deadline notification
    Used with scheduler
    '''
    logger.debug('sending reminder!')
    subs = ''.join(subscribers.get_beautiful_links())
    text = f'Дорогие подпищики: {subs}\n' + f'Дедлайн по {name} : {timestamp_to_date(timestamp)}'
    bot.send_message(chat_id, text, parse_mode="Markdown")


@bot.message_handler(commands=['levo'])
def marks(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    res = """<a href="https://t.me/c/1567266992/88">Ответы</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(
    func=lambda x: x.content_type == 'text' and 
                   get_command_name(x) not in [BotCommand.get, BotCommand.chatid, BotCommand.delete])
def process(message):
    '''
    Process one step of creating new deadline
    '''
    if not check_IDs(message):
        return

    if get_command_name(message) != BotCommand.add and deadline_manager.last_query.get((message.from_user.id, message.chat.id)) is None:
        return

    if (new_deadline := deadline_manager.update(bot, message)) is not None:
        with open(config.PATH_CHAT_DATA.format(message.chat.id), newline='', mode='a') as file:
            file.write('\n' + ','.join([str(new_deadline.timestamp), new_deadline.text, new_deadline.url]))
        scheduler.add_job(add_reminder, 'date',
                          run_date=max(datetime.datetime.fromtimestamp(new_deadline.timestamp, tz=config.TIMEZONE) - datetime.timedelta(hours=1),
                                       datetime.datetime.now(tz=config.TIMEZONE)),
                          args=[new_deadline.text, new_deadline.timestamp, message.chat.id])

def process_deadlines(chat_id):
    '''
    Add existing deadlines for chat: chat_id to scheduler
    '''
    for deadline in get_active_deadlines(chat_id):
        print(deadline)
        scheduler.add_job(add_reminder, 'date',
                          run_date=max(datetime.datetime.fromtimestamp(deadline.timestamp, tz=config.TIMEZONE) - datetime.timedelta(hours=1),
                                       datetime.datetime.now(tz=config.TIMEZONE)),
                          args=[deadline.text, deadline.timestamp, chat_id])

def load_IDs():
    '''
    Load correct IDs
    '''
    with open(config.PATH_IDS, 'r') as fin:
        for line in fin:
            if not line:
                continue
            CORRECT_IDs.append(int(line))


def initial_setup(debug=False):
    '''
    Setup logger & add existing deadlines to scheduler
    '''
    if debug:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    logger.info("hseami213_bot")
    scheduler.start()
    load_IDs()
    for chat_id in CORRECT_IDs:
        process_deadlines(chat_id)


if __name__ == "__main__":
    initial_setup(debug=True)
    bot.infinity_polling()
