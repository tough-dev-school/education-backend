from django.template.defaultfilters import slugify as django_slugify

alphabet = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "j",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ы": "i",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def slugify(string_to_slug: str) -> str:
    """
    Overriding django slugify that allows to use russian words as well.
    """
    return django_slugify("".join(alphabet.get(letter, letter) for letter in string_to_slug.lower()))


def lower_first(string: str) -> str:
    return string[0].lower() + string[1:]
