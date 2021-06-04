from app.conf.environ import env

ABSOLUTE_HOST = env('ABSOLUTE_HOST', cast=str, default='https://edu-app.borshev.com')
ALLOWED_HOSTS = [
    'education-backend.herokuapp.com',
    'edu-app.borshev.com',
    'localhost',
    'localhost:8000',
    'education.borshev.com',
    ABSOLUTE_HOST.replace('https://', ''),
]

CSRF_TRUSTED_ORIGINS = [
    'education.borshev.com',
    'borshev.com',
]
CORS_ALLOWED_ORIGINS = [
    'https://education.borshev.com',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    r'.*education-frontend.netlify.app.*',
]

FRONTEND_URL = env('FRONTEND_URL', cast=str, default='https://education.borshev.com/lms/')
DIPLOMA_FRONTEND_URL = env('DIPLOMA_FRONTEND_URL', cast=str, default='https://certificates.borshev.com/')
