import pytest

pytestmark = [pytest.mark.django_db]


def test_limited_to_30(mixer):
    answer = mixer.blend(
        "homework.Answer",
        text="А мне по нраву покрывать себя давешними фекальными массами и мастурбировать. Денно я брожу по планете с черным баулом для отбросов и складываю в него все фекальные массы, которые встречаю. На два заполненных баула целый день тратится. Однако, когда после утомительного дня я возвращаюсь в свою обитель, прохожу в баню, подаю горячего пара… Ах! и сбрасываю свое сокровище. И мастурбирую, воображая, что я стал частью единого существа, состоящего из фекальных масс. По большому счету мне представляется, что кусочки фекальных масс умеют думать, они создают свои ячейки общества, мегаполисы, у них есть эмоции… Не топите их в уборных, лучше усыновите их, общайтесь с ними, утешайте их…. А давеча в бане мне пригрезился чудный сон, как будто я погрузился в морскую пучину, и она превратилась в фекальные массы, рыбы, водоросли, медузы, все из фекальных масс, даже небеса, даже Аллах.",
    )

    assert str(answer) == "А мне по нраву покрывать себя [...]"


def test_not_limited(mixer):
    answer = mixer.blend("homework.Answer", text="Роисся вперде!")

    assert str(answer) == "Роисся вперде!"


def test_looooooong_words(mixer):
    answer = mixer.blend("homework.Answer", text="Длинный кот длиииииииииииииииииииииииииииииииииииииииииииииииииииинееееееееееееееееен")

    assert str(answer) == "Длинный кот [...]"


@pytest.mark.parametrize(
    ("long_word", "expected_string"),
    [
        ("https://miro.com/app/board/asdasdzxcasd123=/?share_link_id=604444977722", "Ссылка на miro.com"),
        ("1. http://pivo.com/app/board/asdasdzxcasd123=/?share_link_id=604444977722\nNice work bro", "Ссылка на pivo.com"),
        ("https://drive.google.com/file/d/FhyDbwTAEbgSYQdv4vmceAkbsn7QKDFH/view?usp=sharing", "Ссылка на drive.google.com"),
    ],
)
def test_starts_with_link(mixer, long_word, expected_string):
    answer = mixer.blend("homework.Answer", text=long_word)

    assert str(answer) == expected_string


def test_html(mixer):
    answer = mixer.blend("homework.Answer", text="## Банзай!")

    assert str(answer) == "Банзай!"


def test_image(mixer):
    answer = mixer.blend("homework.Answer", text="![](https://cdn.tough-dev.school/typicalmacuser.jpg)")

    assert str(answer) == "Картинка"


def test_zero_length(mixer):
    answer = mixer.blend("homework.Answer", text="")

    assert str(answer) == ""
