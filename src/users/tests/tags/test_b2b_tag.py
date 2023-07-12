import pytest

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize("domain", ["mail.ru", "gmail.com", "yandex.ru"])
def test_with_common_domain(user, domain):
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
