from models import *
from util import *


class DeadlineManager:
    MAX_QUERIES_WITHOUT_CLEANUP = 100
    MAX_QUERY_LIFETIME = 15

    def __init__(self):
        self.last_query_add = {}
        self.last_query_delete = {}
        self.queries_without_cleanup = 0

    def cleanup(self, key):
        flag = self.last_query_add.get(key) is not None or self.last_query_delete.get(key) is not None
        new_dict = {}
        for (user, chat), (*other, timestamp) in self.last_query_add.items():
            if time.time() - timestamp <= DeadlineManager.MAX_QUERY_LIFETIME:
                new_dict[(user, chat)] = [*other, timestamp]
        self.last_query_add = new_dict

        new_dict = {}
        for (user, chat), (*other, timestamp) in self.last_query_delete.items():
            if time.time() - timestamp <= DeadlineManager.MAX_QUERY_LIFETIME:
                new_dict[(user, chat)] = [*other, timestamp]
        self.last_query_delete = new_dict

        return flag and self.last_query_add.get(key) is None and self.last_query_delete.get(key) is None

    @staticmethod
    def ask_add(bot, condition, message):
        if condition == ConditionAdd.TEXT:
            bot.reply_to(message, 'Название дисциплины?')
        elif condition == ConditionAdd.DATE:
            bot.reply_to(message, 'Дедлайн? (dd.mm.yyyy hh:mm)?')
        elif condition == ConditionAdd.URL:
            bot.reply_to(message, 'Ссылочку бы...')
        elif condition == ConditionAdd.DONE:
            bot.reply_to(message, 'Записано')
    
    @staticmethod
    def ask_delete(bot, condition, message, **kwargs):
        if condition == ConditionDelete.ASK:
            res = 'Выберите, какую запись удалить:\n\n'
            for i, deadline in enumerate(get_all_deadlines(message.chat.id)):
                res += str(i) + " :: " + deadline.text + '\n'
            bot.reply_to(message, res, disable_web_page_preview=True)
        elif condition == ConditionDelete.DONE:
            if kwargs.get('success', True):
                bot.reply_to(message, 'Done')
            else:
                bot.reply_to(message, 'Entry not found')

    def add(self, bot, message):
        user, chat = parse_message(message)
        key = (user, chat)
        if self.cleanup(key):
            return
        cur = self.last_query_add.get(key, None)
        message_text = message.text.strip()
        try:
            if cur is None:
                self.last_query_add[key] = [Deadline(), ConditionAdd.NEW, time.time()]
                cur = self.last_query_add[key]
            elif cur[1] == ConditionAdd.TEXT:
                cur[0].set('text', message_text)
            elif cur[1] == ConditionAdd.DATE:
                cur[0].set('timestamp', int(date_to_timestamp(message_text)))
            elif cur[1] == ConditionAdd.URL:
                if message_text.lower() not in ['no', 'нет', 'не', 'неа', 'не-а', '-'] and 'не' not in message_text.lower():
                    cur[0].set('url', message_text)

            cur[1] = ConditionAdd(cur[1] + 1)
            if (cur[1] == ConditionAdd.DONE):
                new_deadline = cur[0]
                with open(config.PATH_CHAT_DATA.format(chat), newline='', mode='a') as file:
                    file.write(','.join([str(new_deadline.timestamp), new_deadline.text, new_deadline.url]) + '\n')
                    schedule_reminder(new_deadline, chat)
                del self.last_query_add[key]
            DeadlineManager.ask_add(bot, cur[1], message)
        except Exception as e:
            logger.error(e)
            bot.reply_to(message, 'Sorry, it seems it a DDOS attack')

    def delete(self, bot, message):
        user, chat = parse_message(message)
        key = (user, chat)
        if self.cleanup(key):
            return
        cur = self.last_query_delete.get(key, None)
        message_text = message.text.strip()
        try:
            if cur is None:
                self.last_query_delete[key] = [0, ConditionDelete.NEW, time.time()]
                cur = self.last_query_delete[key]
            elif cur[1] == ConditionDelete.ASK:
                cur[0] = int(message_text)

            cur[1] = ConditionDelete(cur[1] + 1)
            success = False
            if (cur[1] == ConditionDelete.DONE):
                with open(config.PATH_CHAT_DATA.format(chat), newline='', mode='r') as fin:
                    lines = fin.readlines()
                logger.info(lines)
                with open(config.PATH_CHAT_DATA.format(chat), newline='', mode='w') as fout:
                    for index, line in enumerate(lines):
                        if index == cur[0]:
                            success = True
                            continue
                        fout.write(line)
                del self.last_query_delete[key]

            DeadlineManager.ask_delete(bot, cur[1], message, success=success)
        except Exception as e:
            logger.error(e)
            bot.reply_to(message, 'Sorry, it seems it a DDOS attack')

    def has_active_add(self, message):
        user, chat = parse_message(message)
        key = (user, chat)
        return self.last_query_add.get(key) is not None
    

    def has_active_delete(self, message):
        user, chat = parse_message(message)
        key = (user, chat)
        return self.last_query_delete.get(key) is not None
