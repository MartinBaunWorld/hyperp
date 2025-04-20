# Hyperp

hyperp  will make your life easier by having simple utility functions ready.


## Documentation by example

```python
# -- to_int: Convert to int, or return default on failure --
from hyperp import to_int

to_int("42", 0)     # 42
to_int("x", 0)      # 0
to_int(None, -1)    # -1

# -- is_int: Check if input is an integer --
from hyperp import is_int

is_int("123")       # True
is_int("abc")       # False

# -- is_float: Check if input is a float --
from hyperp import is_float

is_float("3.14")    # True
is_float("hello")   # False

# -- is_ip4: Check if input is a valid IPv4 address --
from hyperp import is_ip4

is_ip4("192.168.1.1")   # True
is_ip4("999.999.0.1")   # False

# -- mkdir: Create a directory and all parents if needed --
from hyperp import mkdir

mkdir("path/to/dir")

# -- mkdir_file: Create parent directories for a file path --
from hyperp import mkdir_file

mkdir_file("logs/output.log")  # Creates the 'logs' directory if missing

# -- write: Write string data to a file, creating dirs if needed --
from hyperp import write

write("out/data.txt", "hello world")

# -- read: Read a file, return default on error --
from hyperp import read

read("out/data.txt", "default")    # "hello world" or "default" if not found

# -- rmdir: Remove a directory and its contents, ignore errors --
from hyperp import rmdir

rmdir("path/to/remove")

# -- sanitize: Make filename safe for storage/use --
from hyperp import sanitize

sanitize("my*unsafe:file?.txt")    # "myunsafefile.txt"

# -- send_file: Upload file to a URL as multipart/form-data --
from hyperp import send_file

send_file("https://example.com/upload", "report.pdf")  # Returns dict with msg and response
```
