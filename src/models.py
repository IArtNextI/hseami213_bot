import config

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

class ConditionAdd(IntEnum):
    NEW = 1
    TEXT = 2
    DATE = 3
    URL = 4
    DONE = 5

class ConditionDelete(IntEnum):
    NEW = 1
    ASK = 2
    DONE = 3

class ConditionChange(IntEnum):
    NEW = 1
    ASK = 2
    ASKFORNEWDEADLINE = 3

    DONE = 4
