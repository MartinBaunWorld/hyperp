
from hyperp import mkdir_file

def write(path, data):
    mkdir_file(path)
    with open(path, "w") as f:
        f.write(data)
