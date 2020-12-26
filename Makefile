fetchdb:
	scp borshev.com:/srv/pmdaily/storage/pmdaily.sqlite storage/
	cd src && ./manage.py anonymize_db

runserver:
	cd src && ./manage.py runserver

lint:
	flake8 src
