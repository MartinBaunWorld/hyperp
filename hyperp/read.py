
def read(path, default):
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return default

