import re
import unicodedata
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


def sanitize(filename):
    """Return a fairly safe version of the filename.

    We don't limit ourselves to ascii, because we want to keep municipality
    names, etc, but we do want to get rid of anything potentially harmful,
    and make sure we do not exceed Windows filename length limits.
    Hence a less safe blacklist, rather than a whitelist.
    """
    blacklist = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|", "\0"]
    reserved = [
        "CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5",
        "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
        "LPT6", "LPT7", "LPT8", "LPT9",
    ]  # Reserved words on Windows
    filename = "".join(c for c in filename if c not in blacklist)
    # Remove all charcters below code point 32
    filename = "".join(c for c in filename if 31 < ord(c))
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.rstrip(". ")  # Windows does not allow these at end
    filename = filename.strip()
    if all([x == "." for x in filename]):
        filename = "__" + filename
    if filename in reserved:
        filename = "__" + filename
    if len(filename) == 0:
        filename = "__"
    if len(filename) > 255:
        parts = re.split(r"/|\\", filename)[-1].split(".")
        if len(parts) > 1:
            ext = "." + parts.pop()
            filename = filename[:-len(ext)]
        else:
            ext = ""
        if filename == "":
            filename = "__"
        if len(ext) > 254:
            ext = ext[254:]
        maxl = 255 - len(ext)
        filename = filename[:maxl]
        filename = filename + ext
        # Re-check last character (if there was no extension)
        filename = filename.rstrip(". ")
        if len(filename) == 0:
            filename = "__"
    return filename


def mkdir(path):
    return pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def mkdir_file(file_path):
    return (
        pathlib.
        Path(file_path).
        parent.
        mkdir(parents=True, exist_ok=True))


def rmdir(path):
    shutil.rmtree(path, ignore_errors=True)


def to_date(txt, default):
    try:
        return datetime.strptime(txt, "%Y-%m-%d")
    except:
        return default


def to_int(num, default):
    try:
        return int(num)
    except: # noqa
        return default


def is_int(num):
    try:
        int(num)
        return True
    except: # noqa
        return False


def is_float(num):
    try:
        float(num)
        return True
    except: # noqa
        return False


def is_ip4(address: str) -> bool:
    if isinstance(address, str):
        pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
        return re.match(pattern, address) is not None
    return False


def runcron(kvdb, name, func, on_error):
    if name not in kvdb:
        kvdb[name] = "0"

    if kvdb[name] == "11":
        on_error(f'Cron {name} tried to run 11 times without fail')
        return
    elif int(kvdb[name]) > 0:
        print("Cronjob is running already. Exit.")
        kvdb[name] = str(int(kvdb[name]) + 1)
        return

    try:
        kvdb[name] = "1"
        func()
    except:  # noqa
        print(format_exc())
        on_error(f'Failed cron {name} {format_exc()}')
        return
    finally:
        kvdb[name] = "0"


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


def read(path, default):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return default


def loads(data, default, on_error=None):
    try:
        return json.loads(data)
    except:  # noqa
        if on_error and callable(on_error):
            on_error()
        return default
