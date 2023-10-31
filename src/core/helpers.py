import random
import string


def lower_first(string: str) -> str:
    return string[0].lower() + string[1:]


def random_string(string_length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=string_length))
