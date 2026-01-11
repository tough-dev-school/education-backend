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
    return factory.course(name="Как стать богатым и здоровым")


@pytest.fixture
def order(factory, user, course):
    return factory.order(user=user, item=course, is_paid=True)


def test(order):
    pdf = BytesIO(get_pdf(order.study))
    reader = PdfReader(pdf)

    text = reader.pages[0].extract_text().replace("\n", "")

    # We can assert only by one word, cuz fpdf2 uses space for justification
    assert "Справка" in text, "Document title"
    assert "Сидор" in text, "User first name"
    assert "Петров" in text, "User last name"
    assert f"№ {order.pk}" in text, "Document number"
    assert "богатым" in text, "Course name"
