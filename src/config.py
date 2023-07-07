from datetime import datetime, timezone, timedelta
import os
import pytz

PATH_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_DATA = os.path.join(PATH_BASE, 'data')
PATH_IDS = os.path.join(PATH_DATA, 'additional_IDs')
PATH_SUBSCRIBERS = os.path.join(PATH_DATA, 'subscribers.csv')
PATH_CHAT_DATA = os.path.join(PATH_DATA, 'data_{}.csv')

DEADLINE_FIELDS_TYPES = [int, str, str]

TIMEZONE = timezone(timedelta(hours=3))
TIME_FORMAT = '%d.%m.%Y %H:%M'
EMAIL = 'aakurdun@edu.hse.ru'

BUS_COMMANDS = ['bus', 'avtobus', 'oakpass', 'avtozak', 'partyvan', 'boynextbus']
