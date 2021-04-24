from app.conf.environ import env

MEDIA_URL = env('MEDIA_URL', default='/media/')
