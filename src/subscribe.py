import string

import pandas
import threading
import config
import os

def get_class_members(input_class):
    return [attr for attr in dir(input_class) if not callable(getattr(input_class, attr)) and not attr.startswith("__")]


class Subscriber:
    def __init__(self, userid: int, username: string, emoji: string = '🤡', isSub: bool = False):

        if len(emoji) != 1:
            raise ValueError('When adding Userid = ', userid, ', Username = ', username, ' expected 1 symbol, but found: ', emoji)

        self.Emoji = emoji
        self.Userid = userid
        self.Username = username
        self.IsSub = isSub

    Userid = 0
    Username = 'Clown'
    Emoji = '🤡'
    IsSub = False


class SubscriberHolder:
    def __init__(self, subscribers_filepath = config.PATH_SUBSCRIBERS):
        self. __subscribers_filepath = subscribers_filepath

        self.__subscribers = pandas.read_csv(
              filepath_or_buffer = subscribers_filepath
            , index_col = 'Userid'
            , names = get_class_members(Subscriber) if os.stat(subscribers_filepath).st_size == 0 else None
            , sep='|'
        )

    def get_all(self):
        with self.__subscribersMutex:
            return self.__subscribers

    def get_one(self, userid: int):
        with self.__subscribersMutex:
            return self.__subscribers.loc[userid]

    def get_subs_list(self):
        with self.__subscribersMutex:
            subs_list = list()
            for index, row in self.__subscribers.iterrows():
                if row['IsSub']:
                    subs_list.append(f"{row['Username']}: {row['Emoji']}")
        return subs_list

    def get_beautiful_links(self):
        with self.__subscribersMutex:
            linklist = list()
            for index, row in self.__subscribers.iterrows():
                if row['IsSub']:
                    linklist.append(f"[{row['Emoji']}](tg://user?id={index})")
        return linklist

    def subscribe(self, new_subscriber: Subscriber):
        with self.__subscribersMutex:
            self.__subscribers.loc[new_subscriber.Userid] = {'Username': new_subscriber.Username, 'Emoji': new_subscriber.Emoji, 'IsSub': True}
            self.__subscribers.to_csv(self.__subscribers_filepath, sep='|')

    def unsubscribe(self, unsubscriber: Subscriber):
        with self.__subscribersMutex:
            self.__subscribers.loc[unsubscriber.Userid] = {'Username': unsubscriber.Username, 'Emoji': unsubscriber.Emoji, 'IsSub': False}
            self.__subscribers.to_csv(self.__subscribers_filepath, sep='|')

    __subscribers = pandas.DataFrame
    __subscribersMutex = threading.RLock()
    __subscribers_filepath = config.PATH_SUBSCRIBERS
