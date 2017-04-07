import os
import re
import csv
import datetime
import mimetypes
import scrapy
import subprocess

from django.shortcuts import render
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.conf import settings

from .models import *


@login_required(login_url='/admin/login/')
def init_category(request):
    ALL_CATEGORIES = {
        '/sams/apparel-shoes/1959': 'Apparel & Shoes',
        '/sams/appliances/1004': 'Appliances',
        '/sams/auto-tires/1055': 'Auto & Tires',
        '/sams/baby-supplies/1946': 'Baby',
        '/sams/child-care-supplies-classroom-supplies/2074': 'Child Care & Schools',
        '/sams/cigarettes-tobacco/1580': 'Cigarettes & Tobacco',
        '/sams/computers/1116': 'Computers',
        '/sams/concession-supplies/2046': 'Concession Supplies',
        '/sams/construction-repair/2139': 'Construction & Repair',
        '/sams/convenience-stores-supplies/2043': 'Convenience Stores',
        '/sams/electronics/1086': 'Electronics & Computers',
        '/sams/family-caregiving/15720473': 'Family Caregiving',
        '/sams/foodservice/15770140': 'Foodservice',
        '/sams/furniture/1286': 'Furniture',
        '/sams/gift-cards/1003': 'Gift Cards',
        '/sams/grocery/1444': 'Grocery',
        '/sams/home-collection/1285': 'Home',
        '/sams/home-improvement/1390': 'Home Improvement',
        '/sams/hotel-hospitality/2161': 'Hotel & Hospitality',
        '/sams/janitorial-cleaning/2151': 'Housekeeping & Janitorial Supplies',
        '/sams/in-clubs/1000209': 'In Clubs',
        '/sams/jewelry-flowers-gifts/7520117': 'Jewelry, Flowers & Gifts',
        '/sams/movies-tv-blu-ray-dvd/6120119': 'Movies',
        '/sams/new-items-online/8131': 'New Items',
        '/sams/office-supplies/1706': 'Office',
        '/sams/outdoor-living/1852': 'Outdoor & Patio',
        '/sams/pet-care/2011': 'Pet Care',
        '/sams/health-and-beauty/1585': 'Pharmacy, Health & Beauty',
        '/sams/religious-organizations/2111': 'Religious Organizations',
        '/sams/restaurant-supplies/2209': 'Restaurant Supplies',
        '/sams/salons-barber-shops/2042': 'Salons & Spa',
        '/sams/seasonal-special-occasions/1900101': 'Seasonal & Occasions',
        '/sams/shops-promotions/7130108': 'Shops & Promotions',
        '/sams/sports-equipment-fitness-equipment/1888': 'Sports & Fitness',
        '/sams/start-saving-green/1130105': 'Start Saving Green',
        '/sams/toys-and-video-games/1929': 'Toys & Video Games',
        '/sams/vending-machines-vending-concession/2247': 'Vending Machines' 
    }

    create_category(None, '/', 'All')
    for url, title in ALL_CATEGORIES.items():
        create_category('/', url, title)

    return HttpResponse('Top categories are successfully initiated')


@login_required(login_url='/admin/login/')
def export_products(request):
    if request.method == "POST":
        product_ids = request.POST.get('ids').strip().split(',')
        result_csv_fields = request.POST.getlist('props[]')
        path = datetime.datetime.now().strftime("/tmp/.samsclub_products_%Y_%m_%d_%H_%M_%S.csv")

        if product_ids == [u'']:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(id__in=product_ids)

        write_report(queryset, path, result_csv_fields)
        
        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) # not FileField instance
        response['Content-Disposition'] = 'attachment; filename=%s/' % smart_str( os.path.basename( path ) ) # same here        
        return response
    else:
        fields = [f.name for f in Product._meta.get_fields() 
                  if f.name not in ['updated_at', 'is_new']]
        return render(request, 'product_properties.html', locals())    


def write_report(queryset, path, result_csv_fields):
    result = open(path, 'w')
    result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
    result_csv.writeheader()

    for product in queryset:
        product_ = model_to_dict(product, fields=result_csv_fields)
        for key, val in product_.items():
            if type(val) not in (float, int, long) and val:
                product_[key] = val.encode('utf-8')

        try:
            result_csv.writerow(product_)
        except Exception, e:
            print product_

    result.close()


def get_subcategories(parent='/', title=''):
    """
    return direct child categories
    """
    categories = Category.objects.filter(parent=parent, title__contains=title)
    return [item.url for item in categories]


def create_category(parent, url, title):
    try:
        Category.objects.create(parent_id=parent, url=url, title=title)
    except Exception, e:
        print str(e)


def get_category_products(category, attr='url'):
    """
    param: category as url
    """
    category = Category.objects.get(url=category)
    result = []
    for cate in category.get_all_children():
        for item in Product.objects.filter(category=cate):
            result.append(getattr(item, attr))
    return result


def set_old_category_products(category):
    for cate in category.get_all_children():
        Product.objects.filter(category=cate).update(is_new=False)
