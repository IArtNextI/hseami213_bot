import config
import csv
import datetime
import logging
import pytz
import time
from apscheduler.schedulers.background import BackgroundScheduler

from models import Deadline

# logger
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('hseami213_bot')

# scheduler
scheduler = BackgroundScheduler(timezone=config.TIMEZONE)


def get_all_deadlines(chat_id):
    try:
        with open(config.PATH_CHAT_DATA.format(chat_id), newline='', mode='r') as fin:
            reader = csv.reader(fin)
            res = []
            for row in reader:
                row = [convert(value) for convert, value in zip(config.DEADLINE_FIELDS_TYPES, row)]
                res.append(Deadline(*row))
            return res
    except FileNotFoundError:
        return []


def get_active_deadlines(chat_id):
    return [deadline for deadline in get_all_deadlines(chat_id) if time.time() < deadline.timestamp]


def get_command_name(message):
    return message.text.replace("@hseami213_bot", '').split()[0][1:]


def parse_message(message):
    '''
    returns pair {user_id, chat_id}
    '''
    return message.from_user.id, message.chat.id


def send_reminder(name, timestamp, subscribers, bot, chat_id):
    '''
    Function that sends deadline notification
    Used with scheduler
    '''
    logger.debug('sending reminder!')
    subs = ''.join(subscribers.get_beautiful_links())
    text = f'Дорогие подпищики: {subs}\n' + f'Дедлайн по {name} : {timestamp_to_date(timestamp)}'
    bot.send_message(chat_id, text, parse_mode="Markdown")


def schedule_reminder(new_deadline, chat, subscribers, bot):
    '''
    Schedules send_reminder() call
    '''
    run_date = max(datetime.datetime.fromtimestamp(new_deadline.timestamp, tz=config.TIMEZONE) - datetime.timedelta(hours=1), datetime.datetime.now(tz=config.TIMEZONE))
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=run_date,
        args=[new_deadline.text, new_deadline.timestamp, subscribers, bot, chat]
    )


def timestamp_to_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=pytz.utc).astimezone(config.TIMEZONE).strftime(config.TIME_FORMAT)


def date_to_timestamp(date):
    dt = datetime.datetime.strptime(date, config.TIME_FORMAT)
    dt = dt.replace(tzinfo=config.TIMEZONE)
    dt = dt.astimezone(pytz.utc)
    return int(dt.timestamp())
