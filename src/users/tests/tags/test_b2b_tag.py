import pytest

from mailing.models import PersonalEmailDomain
from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]

default_domains = ["mail.ru", "gmail.com", "yandex.ru"]


@pytest.fixture(autouse=True)
def _default_personal_emails(mixer):  # tests are unstable without this due to default values are populated in migration
    PersonalEmailDomain.objects.all().delete()
    for default_domain in default_domains:
        PersonalEmailDomain.objects.create(name=default_domain)


@pytest.fixture
def new_personal_domain(mixer):
    return lambda name: mixer.blend("mailing.PersonalEmailDomain", name=name)


@pytest.mark.parametrize("domain", ["hehe.xD", "not.company.yep", "pepe.friends"])
def test_with_recently_added_personal_domain(user, new_personal_domain, domain):
    new_personal_domain(domain)
    user.email = f"myemail@{domain}"
    user.save()

    apply_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["mail.ru", "gmail.com", "yandex.ru"])
def test_with_default_personal_domains(user, domain):
    user.email = f"something@{domain}"
    user.save()

    apply_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["yandex-team.ru", "pwc.com", "fands.dev"])
def test_with_company_domain(user, domain):
    user.email = f"nothing@{domain}"
    user.save()

    apply_tags(user)

    assert "b2b" in user.tags


@pytest.mark.parametrize("email", ["", "1:170/918.10", "myname.mail.ru", '"@"@gmail.com', "\\@@ya.ru"])
def test_with_incorrect_email(user, email):
    user.email = email
    user.save()

    apply_tags(user)

    assert "b2b" not in user.tags
