import pytest

pytestmark = [pytest.mark.django_db]

DEFAULT_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
TEST_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

DEFAULT_FROM_EMAIL = 'Donald T <trump@employee.trumphotels.com>'
TEST_FROM_EMAIL = 'Mark Z <zuckerberg@facebook-team.com>'


@pytest.fixture(autouse=True)
def _settings(settings):
    settings.DEBUG = False
    settings.EMAIL_BACKEND = DEFAULT_BACKEND
    settings.DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL


@pytest.fixture
def configuration(mixer):
    return mixer.blend('mailing.EmailConfiguration', backend=TEST_BACKEND, from_email=TEST_FROM_EMAIL, backend_options={})


@pytest.fixture
def get_configuration(mocker):
    return mocker.patch('mailing.owl.get_configuration')


@pytest.fixture
def owl(owl):
    return owl()


def test_default_backend(owl):
    assert owl.backend_name == DEFAULT_BACKEND


def test_default_backend_for_configuration_with_unset_backend(owl, configuration, get_configuration):
    configuration.backend = ''
    get_configuration.return_value = configuration

    assert owl.backend_name == DEFAULT_BACKEND


@pytest.mark.parametrize(('debug', 'expected_backend'), [
    (True, DEFAULT_BACKEND),
    (False, TEST_BACKEND),
])
def test_custom_backend(settings, owl, get_configuration, configuration, debug, expected_backend):
    settings.DEBUG = debug
    get_configuration.return_value = configuration

    assert owl.backend_name == expected_backend


@pytest.mark.parametrize(('debug', 'expected_email'), [
    (True, DEFAULT_FROM_EMAIL),
    (False, TEST_FROM_EMAIL),
])
def test_custom_from_email(settings, owl, get_configuration, configuration, debug, expected_email):
    settings.DEBUG = debug
    get_configuration.return_value = configuration

    assert owl.msg.from_email == expected_email


def test_backend_options_are_applyed(owl, get_configuration, configuration, mocker):
    configuration.backend_options = {'test': '__mocked'}
    get_configuration.return_value = configuration

    backend_init = mocker.patch(f'{TEST_BACKEND}.__init__', return_value=None)

    owl.connection  # call the connection property

    backend_init.assert_called_once_with(fail_silently=False, test='__mocked')
