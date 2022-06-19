from app.conf.environ import env

ATOL_LOGIN = env('ATOL_LOGIN', cast=str, default='')
ATOL_PASSWORD = env('ATOL_PASSWORD', cast=str, default='')
ATOL_GROUP_CODE = env('ATOL_GROUP_CODE', cast=str, default='')
ATOL_PAYMENT_ADDRESS = env('ATOL_PAYMENT_ADDRESS', cast=str, default='')
ATOL_WEBHOOK_SALT = env('ATOL_WEBHOOK_SALT', cast=str, default='')
