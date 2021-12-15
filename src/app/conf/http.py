from app.conf.environ import env

ABSOLUTE_HOST = env('ABSOLUTE_HOST', cast=str, default='https://app.tough-dev.school')
ALLOWED_HOSTS = [
    'localhost',
    'localhost:8000',
    ABSOLUTE_HOST.replace('https://', ''),
]

CSRF_TRUSTED_ORIGINS = [
    'education.borshev.com',
    'borshev.com',
    'tough-dev.school',
]
CORS_ALLOWED_ORIGINS = [
    'https://education.borshev.com',
    'https://certificates.tough-dev.school',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    r'.*education-frontend.netlify.app.*',
]

FRONTEND_URL = env('FRONTEND_URL', cast=str, default='https://lms.tough-dev.school/lms/')
DIPLOMA_FRONTEND_URL = env('DIPLOMA_FRONTEND_URL', cast=str, default='https://cert.tough-dev.school/')
