# celery worker -l info -A start --beat
# ps aux|grep 'celery worker'

from datetime import timedelta
from celery import Celery
from celery.task import periodic_task

import os

app = Celery('tasks', backend='amqp',
             broker='amqp://guest@localhost//')


@periodic_task(run_every=timedelta(minutes=1))
def scrape_samsclub():
    os.system("python celery_crawler.py ALL")
