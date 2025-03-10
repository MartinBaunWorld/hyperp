import base64
import os
from json import loads
from sys import argv

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from hyperp.utils import read


_key = read(".config.key", "").strip()
_config = loads(read(".config.json", "{}"))


def _derive_key(password: str, salt: bytes) -> bytes:
    # Derive a cryptographic key from the password and salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(message: str, password: str) -> str:
    # Generate a random salt
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    cipher = Fernet(key)
    encrypted_message = cipher.encrypt(message.encode())
    # Combine salt and encrypted message and encode to Base64
    return base64.urlsafe_b64encode(salt + encrypted_message).decode()


def decrypt(encrypted_message: str, password: str) -> str:
    # Decode the Base64 encoded message
    encrypted_message = base64.urlsafe_b64decode(encrypted_message)
    # Extract the salt from the encrypted message
    salt = encrypted_message[:16]
    encrypted_message = encrypted_message[16:]
    key = _derive_key(password, salt)
    cipher = Fernet(key)
    decrypted_message = cipher.decrypt(encrypted_message).decode()
    return decrypted_message



def _decrypt_if_needed(msg):
    if msg.startswith("HYPERP_ENCRYPTED:"):
        return decrypt(msg[17:], _key)
    return msg



def get_int(name, default):
    try:
        return int(_config.get(name, default))
    except:
        return int(default)

def get_str(name, default):
    return _decrypt_if_needed(_config.get(name, default))


def get_bool(name, default):
    return _config.get(name, default)


if __name__ == "__main__":
    if len(argv) != 3:
        print("Usage:")
        print("python3 config.py msg password")
        exit(1)
    print(f"Encrypted '{argv[1]}':")
    print("Please put the following in your config.json for the correct environment")
    print(f"HYPERP_ENCRYPTED:{encrypt(argv[1], argv[2])}")
