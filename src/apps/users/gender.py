from typing import TYPE_CHECKING, Literal

from pytrovich.detector import PetrovichGenderDetector
from pytrovich.enums import Case, NamePart
from pytrovich.enums import Gender as PytrovichGender
from pytrovich.maker import PetrovichDeclinationMaker

if TYPE_CHECKING:
    from apps.users.models import User


def get_or_detect_gender(user: "User") -> Literal["male", "female"]:
    if user.gender and len(user.gender):
        return user.gender  # type: ignore[return-value]

    try:
        detected = PetrovichGenderDetector().detect(firstname=user.first_name, lastname=user.last_name)

        if detected == PytrovichGender.FEMALE:
            return "female"

        return "male"

    except StopIteration:
        return "male"  # flex scope


def get_dative_name(user: "User") -> str:
    gender = PytrovichGender.FEMALE if get_or_detect_gender(user) == "female" else PytrovichGender.MALE

    translator = PetrovichDeclinationMaker()

    first_name = translator.make(NamePart.FIRSTNAME, gender, Case.DATIVE, user.first_name)
    last_name = translator.make(NamePart.LASTNAME, gender, Case.DATIVE, user.last_name)

    return f"{first_name} {last_name}"
