import pytest

import httpx

from diplomas.services.diploma_generator import WrongDiplomaServiceResponse

pytestmark = [
    pytest.mark.slow,
    pytest.mark.django_db,
]

RUNS = 0


def generate_exception_n_times(times: int):
    def generator(request):
        global RUNS
        if RUNS < times:
            RUNS += 1

            return httpx.Response(status_code=500)

        return httpx.Response(status_code=200, content=b"TYPICAL MAC USER JPG")

    return generator


@pytest.fixture(autouse=True)
def _reset_runs_count():
    yield

    global RUNS
    RUNS = 0


@pytest.fixture
def generator(generator):
    return generator(language="RU")


def test_ok(generator, httpx_mock):
    httpx_mock.add_callback(generate_exception_n_times(3))

    diploma = generator()

    assert diploma.image.read() == b"TYPICAL MAC USER JPG"


def test_fail(generator, httpx_mock):
    httpx_mock.add_callback(generate_exception_n_times(6))

    with pytest.raises(WrongDiplomaServiceResponse):
        generator()
