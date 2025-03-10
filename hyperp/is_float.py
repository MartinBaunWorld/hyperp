

def is_float(num):
    try:
        float(num)
        return True
    except: # noqa
        return False
