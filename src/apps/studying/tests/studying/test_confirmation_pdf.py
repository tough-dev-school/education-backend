import re
from datetime import date
from io import BytesIO

import pytest
from pypdf import PdfReader

from apps.studying.confirmation.pdf import get_pdf

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(factory):
    user = factory.user()
    user.update(first_name="Сидор", last_name="Петров")

    return user


@pytest.fixture
def course(factory):
    return factory.course(
        name="Как стать богатым и здоровым",
        start_date=date(2032, 12, 15),
        end_date=date(2033, 1, 15),
    )


@pytest.fixture
def order(factory, user, course):
    return factory.order(user=user, item=course, is_paid=True)


def get_text(order) -> str:
    pdf = BytesIO(get_pdf(order.study))
    reader = PdfReader(pdf)

    text = reader.pages[0].extract_text().replace("\n", "")

    return re.sub(r"\s+", " ", text)  # so we could assert multiple wards, cuz fpdf2 uses space for justification


def test(order):
    text = get_text(order)

    assert "Справка" in text, "Document title"
    assert "Выдана Сидору Петрову" in text, "User name in dative"
    assert f"№ ПК-{order.pk}" in text, "Document number"
    assert "богатым и здоровым" in text, "Course name"

    assert "15 декабря 2032" in text
    assert "15 января 2033" in text


def test_female(order):
    order.user.update(first_name="Анна", last_name="Петрова")

    text = get_text(order)

    assert "Выдана Анне Петровой" in text, "User name in dative (female)"
    assert "прослушала" in text, "Femintive"
