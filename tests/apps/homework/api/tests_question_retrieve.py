import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase", "_set_current_user"),
]


def test_ok(api, question):
    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert got["slug"] == str(question.slug)
    assert got["name"] == question.name


def test_markdown(api, question):
    question.update(text="*should be rendered*")

    got = api.get(f"/api/v2/homework/questions/{question.slug}/")

    assert "<em>should be rendered" in got["text"]


def test_403_for_not_purchased_users(api, question, purchase):
    purchase.refund(purchase.price)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=403)


def test_ok_for_superusers_even_when_they_did_not_purchase_the_course(api, question, purchase):
    purchase.refund(purchase.price)

    api.user.update(is_superuser=True)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_ok_for_users_with_permission_even_when_they_did_not_purchase_the_course(api, question, purchase):
    purchase.refund(purchase.price)

    api.user.add_perm("homework.question.see_all_questions")

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_ok_if_user_has_not_purchased_but_permission_check_is_disabled(api, settings, question, purchase):
    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = True
    purchase.refund(purchase.price)

    api.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=200)


def test_no_anon(anon, question):
    anon.get(f"/api/v2/homework/questions/{question.slug}/", expected_status_code=401)
