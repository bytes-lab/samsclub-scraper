import os
import csv
import datetime
import mimetypes
import scrapy

from django.shortcuts import render
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.conf import settings

from samsclub_scraper.celery_crawler import scrape_module
from .models import *


@login_required(login_url='/admin/login/')
def init_category(request):
    ALL_CATEGORIES = {
        'apparel-shoes/1959': 'Apparel & Shoes',
        'appliances/1004': 'Appliances',
        'auto-tires/1055': 'Auto & Tires',
        'baby-supplies/1946': 'Baby',
        'child-care-supplies-classroom-supplies/2074': 'Child Care & Schools',
        'cigarettes-tobacco/1580': 'Cigarettes & Tobacco',
        'computers/1116': 'Computers',
        'concession-supplies/2046': 'Concession Supplies',
        'construction-repair/2139': 'Construction & Repair',
        'convenience-stores-supplies/2043': 'Convenience Stores',
        'electronics/1086': 'Electronics & Computers',
        'family-caregiving/15720473': 'Family Caregiving',
        'foodservice/15770140': 'Foodservice',
        'furniture/1286': 'Furniture',
        'gift-cards/1003': 'Gift Cards',
        'grocery/1444': 'Grocery',
        'home-collection/1285': 'Home',
        'home-improvement/1390': 'Home Improvement',
        'hotel-hospitality/2161': 'Hotel & Hospitality',
        'janitorial-cleaning/2151': 'Housekeeping & Janitorial Supplies',
        'in-clubs/1000209': 'In Clubs',
        'jewelry-flowers-gifts/7520117': 'Jewelry, Flowers & Gifts',
        'movies-tv-blu-ray-dvd/6120119': 'Movies',
        'new-items-online/8131': 'New Items',
        'office-supplies/1706': 'Office',
        'outdoor-living/1852': 'Outdoor & Patio',
        'pet-care/2011': 'Pet Care',
        'health-and-beauty/1585': 'Pharmacy, Health & Beauty',
        'religious-organizations/2111': 'Religious Organizations',
        'restaurant-supplies/2209': 'Restaurant Supplies',
        'salons-barber-shops/2042': 'Salons & Spa',
        'seasonal-special-occasions/1900101': 'Seasonal & Occasions',
        'shops-promotions/7130108': 'Shops & Promotions',
        'sports-equipment-fitness-equipment/1888': 'Sports & Fitness',
        'start-saving-green/1130105': 'Start Saving Green',
        'toys-and-video-games/1929': 'Toys & Video Games',
        'vending-machines-vending-concession/2247': 'Vending Machines' 
    }

    idx = 0
    for url, title in ALL_CATEGORIES.items():
        idx += 1
        item = {
            'url': url, 
            'title': title,
            'code': "{0:0>7}".format(idx)
        }

        Category.objects.update_or_create(url=url, defaults=item)

    return HttpResponse('Top categories are successfully initiated')


@login_required(login_url='/admin/login/')
def export_products(request):
    if request.method == "POST":
        product_ids = request.POST.get('ids').strip().split(',')
        result_csv_fields = request.POST.getlist('props[]')
        new_products = request.POST.get('new_products')

        path = datetime.datetime.now().strftime("/tmp/.samsclub_products_%Y_%m_%d_%H_%M_%S.csv")
        result = open(path, 'w')
        result_csv = csv.DictWriter(result, fieldnames=result_csv_fields)
        result_csv.writeheader()

        if product_ids == [u'']:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(id__in=product_ids)

        if new_products:
            pass
            
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

        wrapper = FileWrapper( open( path, "r" ) )
        content_type = mimetypes.guess_type( path )[0]

        response = HttpResponse(wrapper, content_type = content_type)
        response['Content-Length'] = os.path.getsize( path ) # not FileField instance
        response['Content-Disposition'] = 'attachment; filename=%s/' % smart_str( os.path.basename( path ) ) # same here        
        return response
    else:
        fields = [f.name for f in Product._meta.get_fields() if f.name not in ['updated_at']]
        return render(request, 'product_properties.html', locals())    


def run_scrapy(request):
    path = settings.BASE_DIR+'/samsclub_scraper/'
    os.system("python {}celery_crawler.py 123,324".format(path))
    return HttpResponse('Scraper is completed successfully!')


def get_subcategories(code):
    categories = Category.objects.filter(code__starts_with=code).order_by(code)
    cates = []
    for item in categories:
        cates.append(model_to_dict(item))
    return cates


def save_category(parent_code, url, title):
    if Category.objects.exist(url=url, code__starts_with=parent_code):
        return
    code = generate_code(parent_code)
    Category.objects.create(code=code, url=url, title=title)


def generate_code(parent_code):
    pass
