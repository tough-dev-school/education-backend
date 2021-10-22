web: bin/start-pgbouncer sh -c 'cd src && uwsgi --master --http :$PORT --module app.wsgi --workers 2 --threads 2 --harakiri 25 --max-requests 1000 --log-x-forwarded-for --buffer-size 32000'
worker: cd src && celery -A app worker --beat -Q celery -c 4 -n 'default@%h' --max-tasks-per-child 50
release: cd src && python manage.py migrate && python manage.py invalidate_cachalot
