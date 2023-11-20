import pytest

from apps.users.tags.pipeline import generate_tags
from apps.mailing.models import PersonalEmailDomain

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def new_personal_domain(mixer):
    return lambda name: mixer.blend("mailing.PersonalEmailDomain", name=name)


@pytest.mark.parametrize("domain", ["hehe.xD", "not.company.yep", "pepe.friends"])
def test_with_recently_added_personal_domain(user, new_personal_domain, domain):
    new_personal_domain(domain)
    user.update(email=f"myemail@{domain}")

    generate_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["mail.ru", "gmail.com", "yandex.ru"])
def test_with_default_personal_domains(user, domain):
    user.update(email=f"somemail@{domain}")

    generate_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["yandex-team.ru", "pwc.com", "fands.dev"])
def test_with_company_domain(user, domain):
    user.update(email=f"nothing@{domain}")

    generate_tags(user)

    assert "b2b" in user.tags


@pytest.mark.parametrize("email", ["", "1:170/918.10", "myname.mail.ru", '"@"@gmail.com', "\\@@ya.ru"])
def test_with_incorrect_email(user, email):
    user.update(email=email)

    generate_tags(user)

    assert "b2b" not in user.tags
