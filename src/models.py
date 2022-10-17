import config
from util import *

import datetime
import time
from dataclasses import dataclass
from enum import IntEnum, auto

from config import DEADLINE_FIELDS_TYPES


@dataclass(frozen=False)
class Deadline:
    timestamp: int = 0
    text: str = ''
    url: str = ''

    def set(self, field, value):
        setattr(self, field, value)



class DeadlineManager:
    MAX_QUERIES_WITHOUT_CLEANUP = 100
    MAX_QUERY_LIFETIME = 180

    def __init__(self):
        self.last_query = {}
        self.queries_without_cleanup = 0

    def cleanup(self):
        self.queries_without_cleanup += 1
        if self.queries_without_cleanup >= DeadlineManager.MAX_QUERIES_WITHOUT_CLEANUP:
            self.queries_without_cleanup = 0
            new_dict = {}
            for (user, chat), (deadline, condition, timestamp) in self.last_query.items():
                if time.time() - timestamp <= DeadlineManager.MAX_QUERY_LIFETIME:
                    new_dict[(user, chat)] = [deadline, condition, timestamp]
            self.last_query = new_dict

    @staticmethod
    def ask(bot, condition, message):
        if condition == DeadlineManager.Condition.TEXT:
            bot.reply_to(message, 'Название дисциплины?')
        elif condition == DeadlineManager.Condition.DATE:
            bot.reply_to(message, 'Дедлайн? (dd.mm.yyyy hh:mm)?')
        elif condition == DeadlineManager.Condition.URL:
            bot.reply_to(message, 'Ссылочку бы...')  
        elif condition == DeadlineManager.Condition.DONE:
            bot.reply_to(message, 'Записано')

    def update(self, bot, message):
        self.cleanup()
        user = message.from_user.id
        chat = message.chat.id
        cur = self.last_query.get((user, chat), None)
        message_text = message.text.strip()
        try:
            if cur is None:
                self.last_query[(user, chat)] = [Deadline(), DeadlineManager.Condition.NEW, time.time()]
                cur = self.last_query[(user, chat)]
            elif cur[1] == DeadlineManager.Condition.TEXT:
                cur[0].set('text', message_text)
            elif cur[1] == DeadlineManager.Condition.DATE:
                cur[0].set('timestamp', int(date_to_timestamp(message_text)))
            elif cur[1] == DeadlineManager.Condition.URL:
                if message_text not in ['no', 'нет', 'не', 'неа', 'не-а', '-']:
                    cur[0].set('url', message_text)

            cur[1] = DeadlineManager.Condition(cur[1] + 1)
            data = DeadlineManager.ask(bot, cur[1], message)
            if (cur[1] == DeadlineManager.Condition.DONE):
                del self.last_query[(user, chat)]
                return cur[0]
        except:
            bot.reply_to(message, 'Sorry, it seems it a DDOS attack')
        return None

    class Condition(IntEnum):
        NEW = 1
        TEXT = 2
        DATE = 3
        URL = 4

        DONE = 5
