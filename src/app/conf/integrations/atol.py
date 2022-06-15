from app.conf.environ import env

ATOL_LOGIN = env('ATOL_LOGIN', cast=str, default='')
ATOL_PASSWORD = env('ATOL_PASSWORD', cast=str, default='')
