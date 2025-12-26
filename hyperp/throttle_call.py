import time

_last_called = {}


def throttle_call(func, seconds):
    now = time.time()
    last = _last_called.get(func.__name__, 0)
    
    if now - last >= seconds:
        _last_called[func.__name__] = now
        return func()
    return None
