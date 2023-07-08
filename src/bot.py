from unicodedata import name
from pytz import timezone

import config
import admin
import key
import subscribe
from config_commands import BotCommand
from config_messages import BotMessage
from deadline_manager import DeadlineManager
from models import Deadline
from util import *

import csv
import datetime
import logging
import re
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
queries_without_cleanup = 0

CORRECT_IDs = admin.CORRECT_IDs.copy()
ADMIN_IDs = admin.ADMIN_IDs.copy()

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


@bot.message_handler(commands=[BotCommand.userid, BotCommand.chatid])
def get_info(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    bot.reply_to(message, BotMessage[get_command_name(message)](message))


@bot.message_handler(commands=[BotCommand.wiki, BotCommand.marks, BotCommand.recordings])
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

    res = "If you see this, we fucked up"
    if get_command_name(message) == BotCommand.subs:
        res = "Subscrbers list:\n" + '\n'.join(subscribers.get_subs_list())
    else:
        res = "MEGA PING\\!\\!\\!\n" + ''.join(subscribers.get_beautiful_links())

    bot.reply_to(message, res, parse_mode="MarkdownV2", disable_web_page_preview=True)


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
    global CORRECT_IDs
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
    global CORRECT_IDs
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        result = ''
        for index, line in enumerate(list(set(CORRECT_IDs))):
            result += "--> " + str(line) + '\n'
        bot.reply_to(message, result)
    except Exception as e:
        logger.error(e)


@bot.message_handler(commands=['delid'])
def add_ID(message):
    global CORRECT_IDs
    if message.from_user.id not in ADMIN_IDs:
        return
    try:
        candidate_id = int(message.text.split()[1])
        CORRECT_IDs_set = set(CORRECT_IDs)
        CORRECT_IDs_set.remove(candidate_id)
        CORRECT_IDs = list(CORRECT_IDs_set)
        with open(config.PATH_IDS, 'w') as fout:
            print(*CORRECT_IDs_set, sep='\n', file=fout)
        bot.reply_to(message, "Done")
    except Exception as e:
        logger.error(e)


@bot.message_handler(
    func=lambda x: get_command_name(x) == BotCommand.delete or deadline_manager.has_active_delete(x)
)
def delete(message):
    global CORRECT_IDs
    if message.from_user.id not in ADMIN_IDs:
        return

    deadline_manager.delete(bot, message)


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


@bot.message_handler(commands=['levo'])
def marks(message):
    global last_query, CORRECT_IDs
    cleanup()
    if not check_IDs(message):
        return
    res = """<a href="https://t.me/c/1567266992/88">Ответы</a>"""
    bot.reply_to(message, res, parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(
    func=lambda x: get_command_name(x) == BotCommand.add or deadline_manager.has_active_add(x)
)
def add(message):
    '''
    Process one step of creating new deadline
    '''
    if not check_IDs(message):
        return

    deadline_manager.add(bot, subscribers, message)

@bot.message_handler(
    func=lambda x: get_command_name(x) == BotCommand.change or deadline_manager.has_active_change(x)
)
def change(message):
    '''
    Process one step of creating new deadline
    '''
    if not check_IDs(message):
        return

    deadline_manager.change(bot, message)

def process_deadlines(chat_id):
    '''
    Add existing deadlines for chat: chat_id to scheduler
    '''
    for deadline in get_active_deadlines(chat_id):
        logger.info(deadline)
        schedule_reminder(deadline, chat_id, subscribers, bot)


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
