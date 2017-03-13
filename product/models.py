from __future__ import unicode_literals

from django.db import models

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
    category = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField()
    min_quantity = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title
