## Samsclub Product Scraper and Export Project

#### Install python2.7
#### Install project
	git clone <repo>
	apt-get install python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
	pip install -r requirements.txt

#### Migrate the database:
	python manage.py makemigrations product
	python manage.py migrate

#### Create a superuser
	python manage.py createsuperuser

#### Run the project:
	cd Product-Scraper/
	nohup python manage.py runserver 0.0.0.0:80 < /dev/null &

#### Install RabbitMQ

	apt-get update
	apt-get install rabbitmq-server

#### Install PhantomJS
	Ref: [https://gist.github.com/rahularyan/ff4619c435f8bb94ef5b]

	apt-get update
	apt-get install build-essential chrpath libssl-dev libxft-dev
	apt-get install libfreetype6 libfreetype6-dev
	apt-get install libfontconfig1 libfontconfig1-dev
	cd ~
	export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
	wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
	sudo tar xvjf $PHANTOM_JS.tar.bz2
	sudo mv $PHANTOM_JS /usr/local/share
	sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
	phantomjs --version

#### Run celery for store products and scraping:
	cd smasclub_site/samsclub_scraper/samsclub_scraper
	export C_FORCE_ROOT="true"
	celery -A tasks worker --loglevel=info

#### Add a cron entry
	
	* * * * * python /root/cron_task.py

#### Kill workers:
	ps aux|grep 'celery worker'
	kill <pid>s
