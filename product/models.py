from __future__ import unicode_literals

import os
import subprocess

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Category(models.Model):    
    url = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=100)
    parent = models.ForeignKey('Category', null=True)

    def __unicode__(self):
        return self.title

    def get_all_children(self, include_self=True):
        r = []
        if include_self:
            r.append(self)
        for c in Category.objects.filter(parent=self):
            _r = c.get_all_children(include_self=True)
            if 0 < len(_r):
                r.extend(_r)
        return r


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=250)
    price = models.CharField(max_length=10)
    picture = models.CharField(max_length=250)
    rating = models.FloatField()
    review_count = models.IntegerField()
    delivery_time = models.TextField(null=True, blank=True)
    bullet_points = models.TextField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    promo = models.TextField(null=True, blank=True)
    special = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category)
    quantity = models.IntegerField()
    min_quantity = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=200)
    revision = models.IntegerField(default=0)
    is_available = models.BooleanField()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.revision= self.revision + 1
        self.is_available = True
        super(Product, self).save(*args, **kwargs)


MODE = (
    # (0, 'One Time'),
    (1, 'Category'),
    (2, 'Products')
)

STATUS = (
    (0, 'To be started'),
    (1, 'Running'),
    (2, 'To be stoped'),
    (3, 'Stoped'),      # ready for export
    (4, 'Interval')
)

class ScrapyTask(models.Model):
    title = models.CharField(max_length=50)
    mode = models.IntegerField(choices=MODE)
    status = models.IntegerField(choices=STATUS)
    category = models.ForeignKey(Category, blank=True, null=True)
    products = models.TextField(blank=True, null=True)
    interval = models.PositiveIntegerField(validators=[MinValueValidator(5)],
                                           default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.status = 1
            super(ScrapyTask, self).save(*args, **kwargs)
            self.run_scraper()

    def update(self):
        super(ScrapyTask, self).save()

    def delete(self, *args, **kwargs):
        self.status = 3
        self.update()
            # super(ScrapyTask, self).delete(*args, **kwargs)

    def run_scraper(self):
        print "python {}/samsclub_scraper/celery_crawler.py {} {} {} {}" \
                  .format(settings.BASE_DIR, self.pk, self.mode, 
                          self.category_id or 'None', 
                          self.products or 'None'), '@@@@@@@@@@@'
        path = '{}/samsclub_scraper/celery_crawler.py'.format(settings.BASE_DIR)
        subprocess.Popen(["python", 
                          path, 
                          str(self.pk), 
                          str(self.mode), 
                          self.category_id or 'None', 
                          self.products or 'None'])

        # os.system("python {}/samsclub_scraper/celery_crawler.py {} {} {} {}" \
        #           .format(settings.BASE_DIR, 22, self.mode, 
        #                   self.category_id or 'None', 
        #                   self.products or 'None'))
