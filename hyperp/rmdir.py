import shutil

def rmdir(path):
    shutil.rmtree(path, ignore_errors=True)
