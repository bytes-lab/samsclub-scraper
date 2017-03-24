from __future__ import unicode_literals

from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    parent = models.ForeignKey('Category', null=True)

    def __unicode__(self):
        return self.title


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
