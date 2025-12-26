# Hyperp - hyper productive utility functions for Python
Hyperp is a small utility library designed to simplify everyday coding tasks.  
It embraces safe defaults over exceptions — for example, `read()` returns a default value if the file can't be read, helping you gracefully handle edge cases without extra boilerplate.

# Purpose
I run a software consultancy where we build products for clients and internal projects.  
To stay Hyper Productive (hence "hyperp"), I created this library to streamline development and encourage safer patterns.  
It also helps my team write more robust code with minimal effort.

Need simple, beautiful software frontend, backend or design? Checkout [BaunIT.com](https://baunit.com)

## General Utility Functions
Documentation by example
```python
from hyperp import *

# to_int: Convert to int, or return default on failure
to_int("42", 0)     # 42
to_int("x", 0)      # 0
to_int(None, -1)    # -1

# is_int: Check if input is an integer
is_int("123")       # True
is_int("abc")       # False

# is_float: Check if input is a float
is_float("3.14")    # True
is_float("hello")   # False

# is_ip4: Check if input is a valid IPv4 address
is_ip4("192.168.1.1")   # True
is_ip4("999.999.0.1")   # False

# mkdir: Create a directory and all parents if needed
mkdir("path/to/dir")

# mkdir_file: Create parent directories for a file path
mkdir_file("logs/output.log")  # Creates the 'logs' directory if missing

# write: Write string data to a file, creating dirs if needed
write("out/data.txt", "hello world")

# read: Read a file, return default on error
read("out/data.txt", "default")    # "hello world" or "default" if not found

# rmdir: Remove a directory and its contents, ignore errors
rmdir("path/to/remove")

# sanitize: Make filename safe for storage/use
sanitize("my*unsafe:file?.txt")    # "myunsafefile.txt"

# send_file: Upload file to a URL as multipart/form-data
send_file("https://example.com/upload", "report.pdf")  # Returns dict with msg and response

# download: Download file from URL to disk, streaming for efficiency
download("https://example.com/image.jpg", "images/photo.jpg")  # Returns "images/photo.jpg"
download("https://bad-url.com/file.pdf", "out.pdf", "")        # Returns "" on error

# throttle_call: Limit function execution to once per N seconds
def load_data():
    return fetch_from_api()

throttle_call(load_data, 5)  # Executes
throttle_call(load_data, 5)  # Returns None (too soon)
time.sleep(5)
throttle_call(load_data, 5)  # Executes again

# timer: Decorator to measure function execution time
@timer
def slow_function():
    time.sleep(1)
    return "done"

slow_function()  # Prints: "slow_function took 1.0001 seconds"
```

## Django specific
Documentation by example
```python3
from hyperp.django import *

# cache: Shorthand for Django's cache_control with flexible time units
@cache(seconds=30, minutes=5, hours=1, days=1, public=False)
def my_view(request):
    ...

# get_csrf: Return CSRF token input element for forms
def form_view(request):
    csrf = get_csrf(request)
    return HttpResponse(f"<form>{csrf}<input name='x'></form>")

# get_ip: Extract client IP address from request headers
def log_request(request):
    ip = get_ip(request)
    # Use the IP (e.g., for logging, rate limiting, etc.)
```
