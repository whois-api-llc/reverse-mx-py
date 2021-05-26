import copy
import datetime
import re

from .base import BaseModel
import sys

if sys.version_info < (3, 9):
    import typing


_re_date_format = re.compile(r'^\d\d\d\d-\d\d-\d\d$')


def _date_value(values: dict, key: str) -> datetime.date or None:
    if key in values and values[key] is not None:
        if _re_date_format.match(values[key]) is not None:
            return datetime.datetime.strptime(
                values[key], '%Y-%m-%d').date()

    return None


def _string_value(values: dict, key: str) -> str:
    if key in values:
        return str(values[key])
    return ''


def _int_value(values: dict, key: str) -> int:
    if key in values:
        return int(values[key])
    return 0


def _list_value(values: dict, key: str) -> list:
    if key in values and type(values[key]) is list:
        return copy.deepcopy(values[key])
    return []


def _list_of_objects(values: dict, key: str, classname: str) -> list:
    r = []
    if key in values and type(values[key]) is list:
        r = [globals()[classname](x) for x in values[key]]
    return r


def _timestamp2datetime(timestamp: int) -> datetime.datetime or None:
    if timestamp is not None:
        return datetime.datetime.fromtimestamp(timestamp)
    return None


class Result(BaseModel):
    name: str
    first_seen: datetime.datetime or None
    last_visit: datetime.datetime or None

    def __init__(self, values):
        super().__init__()

        self.name = ''
        self.first_seen = ''
        self.last_visit = None

        if values is not None:
            self.name = _string_value(values, 'name')
            self.first_seen = _timestamp2datetime(
                _int_value(values, 'first_seen'))
            self.last_visit = _timestamp2datetime(
                _int_value(values, 'last_visit'))


class Response(BaseModel):
    _PAGE_SIZE = 300

    size: int
    current_page: str
    if sys.version_info < (3, 9):
        result: typing.List[Result]
    else:
        result: [Result]

    def __init__(self, values):
        super().__init__()

        self.size = 0
        self.current_page = '0'
        self.result = []

        if values is not None:
            self.size = _int_value(values, 'size')
            self.current_page = _string_value(values, 'current_page')
            self.result = _list_of_objects(
                values, 'result', 'Result')

    def has_next(self) -> bool:
        """
        Checks if there are a next page
        """
        return self.size >= Response._PAGE_SIZE


class ErrorMessage(BaseModel):
    code: int
    message: str

    def __init__(self, values):
        super().__init__()

        self.int = 0
        self.message = ''

        if values is not None:
            self.code = _int_value(values, 'code')
            self.message = _string_value(values, 'messages')
