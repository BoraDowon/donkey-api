import random
import string
import base64
from Crypto.Cipher import AES

from django.conf import settings


def random_digit_and_number(length_of_value=7):
    choices = string.ascii_uppercase + string.digits + string.ascii_lowercase
    random_value = ''.join(random.SystemRandom().choice(choices) for _ in range(length_of_value))
    return random_value

def random_number(length_of_value=6):
    choices = string.digits
    random_value = ''.join(random.SystemRandom().choice(choices) for _ in range(length_of_value))
    return random_value


class UserCrypto:
    def __init__(self):
        BLOCK_SIZE = 32
        PADDING = '|'
        secret_key = settings.SECRET_KEY[:32]
        cipher = AES.new(secret_key)

        pad = lambda s: s + (BLOCK_SIZE - len(s.encode('utf-8')) % BLOCK_SIZE) * PADDING

        self.encode = lambda s: base64.b64encode(cipher.encrypt(pad(s)))
        self.decode = lambda e: cipher.decrypt(base64.b64decode(e)).decode("utf-8").rstrip(PADDING)

    # TODO: why don't we change to static method?
    def encode(self, data):
        encoded = self.encode(data)
        return encoded

    # TODO: why don't we change to static method?
    def decode(self, data):
        decoded = self.decode(data)
        return decoded
