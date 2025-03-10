import pathlib


def mkdir(path):
    return pathlib.Path(path).mkdir(parents=True, exist_ok=True)

