import pytest

from users.tags.pipeline import generate_tags

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def new_personal_domain(mixer):
    return lambda name: mixer.blend("mailing.PersonalEmailDomain", name=name)


@pytest.mark.parametrize("domain", ["hehe.xD", "not.company.yep", "pepe.friends"])
def test_with_recently_added_personal_domain(user, new_personal_domain, domain):
    new_personal_domain(domain)
    user.email = f"myemail@{domain}"
    user.save()

    generate_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["mail.ru", "gmail.com", "yandex.ru"])
def test_with_default_personal_domains(user, domain):
    user.email = f"something@{domain}"
    user.save()

    generate_tags(user)

    assert "b2b" not in user.tags


@pytest.mark.parametrize("domain", ["yandex-team.ru", "pwc.com", "fands.dev"])
def test_with_company_domain(user, domain):
    user.email = f"nothing@{domain}"
    user.save()

    generate_tags(user)

    assert "b2b" in user.tags


@pytest.mark.parametrize("email", ["", "1:170/918.10", "myname.mail.ru", '"@"@gmail.com', "\\@@ya.ru"])
def test_with_incorrect_email(user, email):
    user.email = email
    user.save()

    generate_tags(user)

    assert "b2b" not in user.tags
