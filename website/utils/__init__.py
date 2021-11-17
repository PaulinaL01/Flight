from string import ascii_letters
from random import choice


def create_code(size):
    return "".join([choice(ascii_letters) for i in range(size)])