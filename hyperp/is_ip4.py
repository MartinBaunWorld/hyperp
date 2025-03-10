import re


def is_ip4(address: str) -> bool:
    if isinstance(address, str):
        pattern = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
        return re.match(pattern, address) is not None
    return False
