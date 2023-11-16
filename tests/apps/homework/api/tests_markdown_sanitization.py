import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("<script>Ev1l</script>", "<!-- raw HTML omitted -->"),
        ("*should be rendered*", "<p><em>should be rendered</em></p>"),
        ("![](typicalmacuser.jpg)", '<p><img src="typicalmacuser.jpg" alt=""></p>'),
        ('<em ev1l="hax0r">test</em>', "<p><!-- raw HTML omitted -->test<!-- raw HTML omitted --></p>"),
        ("a\nb", "<p>a\nb</p>"),
        ("<h1><h2><h3><h4><h5>", "<!-- raw HTML omitted -->"),
        ("# test", "<h1>test</h1>"),
        ("a<hr>b", "<p>a<!-- raw HTML omitted -->b</p>"),
        ("> а хули ты?", "<blockquote>\n<p>а хули ты?</p>\n</blockquote>"),
    ],
)
def test_markdown_gets_sanitized(api, answer, text, expected):
    answer.update(text=text)

    got = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert got["text"].strip() == expected
