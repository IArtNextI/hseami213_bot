import config

import datetime


def timestamp_to_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=config.TIMEZONE).strftime(config.TIME_FORMAT)


def date_to_timestamp(date):
    return datetime.datetime.strptime(date, config.TIME_FORMAT).astimezone(config.TIMEZONE).timestamp()