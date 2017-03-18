# celery -A tasks worker --loglevel=info

import os
from os import sys, path
import django
import json
from celery import Celery
from celery.decorators import task

sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samsclub_site.settings")
django.setup()

from product.models import *

app = Celery('tasks', backend='amqp',
             broker='amqp://guest@localhost//')

@app.task
@task(ignore_result=True)
def store_product(item):
    try:
        Product.objects.update_or_create(id=item['id'], defaults=item)
    except Exception, e:
        pass
