## Samsclub Product Scraper and Export Project

#### Install python2.7
#### Install project
	git clone <repo>
	pip install -r requirements.txt

#### Migrate the database:
	python manage makemigrations
	python manage migrate

#### Create a superuser
	python manage createsuperuser

#### Run the project:
	cd Product-Scraper/
	nohup python manage.py runserver 0.0.0.0:80 < /dev/null &

#### Install RabbitMQ

	apt-get update
	apt-get install rabbitmq-server

#### Run celery:
	export C_FORCE_ROOT="true"
	celery worker -l info -A start --beat

#### Kill workers:
	ps aux|grep 'celery worker'
	kill <pid>s
