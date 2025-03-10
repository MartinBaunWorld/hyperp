import re
import pathlib
import shutil
import json
from traceback import format_exc
from datetime import datetime


def check_form(Model, data):
    from pydantic import ValidationError # noqa
    try:
        form = Model(**data)
        return form, None
    except ValidationError as e:
        errors = e.errors()
        return None, errors



def to_date(txt, default):
    try:
        return datetime.strptime(txt, "%Y-%m-%d")
    except:
        return default


def bars2set(txt):
    if txt is None:
        return set()
    return set([o.strip() for o in txt.split("|") if o.strip() != ""])


def set2bars(txt):
    return "|" + "|".join(txt) + "|"


def bars2list(txt):
    if not txt:
        return []
    return list(bars2set(txt))


def list2bars(l):
    if not l:
        return ""
    return set2bars(set(l))


class CustomObject:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class CustomObjectEncoder(json.JSONEncoder):

    def default(self, obj):
        if obj.__class__.__name__ == "datetime":
            return int(obj.timestamp())

        return super().default(obj)


def dumps(obj):
    return json.dumps(obj, cls=CustomObjectEncoder)


class Throttle:
    """
        Throttles an call to a function to max_per_minute
        Can be used to avoid overloading systems
        such as ErrorHandler
    """
    def __init__(self, func, max_per_minute):
        self._recent = []
        self._func = func
        self._max_per_minute = max_per_minute

    def __call__(self, *args, **kwargs):
        current_date = datetime.now()

        self._recent = [
            m for m in self._recent if (current_date - m).total_seconds() <= 60
        ]

        if len(self._recent) < self._max_per_minute:
            self._recent.append(datetime.utcnow())
            self._func(*args, **kwargs)
        else:
            print("Throttled call")


def timestamp(dt):
    if dt and hasattr(dt, 'timestamp'):
        return dt.timestamp()

    return None


def loads(data, default, on_error=None):
    try:
        return json.loads(data)
    except:  # noqa
        if on_error and callable(on_error):
            on_error()
        return default
