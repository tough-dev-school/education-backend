import pytest

from apps.notion.helpers import get_youtube_video_id


@pytest.mark.parametrize(
    "input, expected",
    [
        ("https://youtu.be/1aSDLtmircA", "1aSDLtmircA"),
        ("1aSDLtmircA", None),
        ("https://youtu.be/watch?v=1aSDLtmircA", "1aSDLtmircA"),
        ("https://youtu.be/Vz-dbHfe5d4?si=gTJccaXi7B7BoqOF", "Vz-dbHfe5d4"),
        ("https://www.youtube.com/watch?v=FmIzx00xDmz&list=PLZuAsus9sSrpdana5Mw-jSkNLNSqgfw3x&index=10&ab_channel=100500", "FmIzx00xDmz"),
        ("https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9294be93-51f7-4b61-b330-cdf098234a34/diagrams.mp4", None),
    ],
)
def test(input, expected):
    assert get_youtube_video_id(input) == expected
