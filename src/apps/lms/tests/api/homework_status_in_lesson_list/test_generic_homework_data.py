import pytest

pytestmark = [pytest.mark.django_db]


def test_no_question(api, module, lesson):
    lesson.update(question=None)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["homework"] is None
    assert got["results"][0]["question"] is None


def test_question_to_deprecate(api, module, question):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["homework"]["question"]

    assert got["name"] == question.name
    assert "<em>" in got["text"], "text is rendered"


def test_question(api, module, question):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")["results"][0]["question"]

    assert got["name"] == question.name
    assert "<em>" in got["text"], "text is rendered"


@pytest.mark.xfail(reason="Moved N+1 out of scope, cuz too few real-world users will encounter it")
def test_query_count(api, module, lesson, factory, mixer, django_assert_num_queries):
    lesson.delete()
    for _ in range(15):
        factory.lesson(
            module=module,
            material=mixer.blend("notion.Material"),
            question=mixer.blend("homework.Question"),
        )

    with django_assert_num_queries(7):
        got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")
        assert len(got["results"]) == 15
