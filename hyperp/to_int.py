

def to_int(num, default):
    try:
        return int(num)
    except: # noqa
        return default
