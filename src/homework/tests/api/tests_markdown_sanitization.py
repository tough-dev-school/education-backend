import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.mark.parametrize(('text', 'expected'), [
    ('<script>Ev1l</script>', '&lt;script&gt;Ev1l&lt;/script&gt;'),
    ('*should be rendered*', '<p><em>should be rendered</em></p>'),
    ('![](typicalmacuser.jpg)', '<p><img src="typicalmacuser.jpg"></p>'),
    ('<em ev1l="hax0r">test</em>', '<p><em>test</em></p>'),
])
def test_markdown_gets_sanitized(api, question, answer, text, expected):
    answer.text = text
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/{answer.slug}/')

    assert got['text'] == expected
