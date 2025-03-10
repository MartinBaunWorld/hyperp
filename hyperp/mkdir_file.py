import pathlib

def mkdir_file(file_path):
    return (
        pathlib.
        Path(file_path).
        parent.
        mkdir(parents=True, exist_ok=True))
