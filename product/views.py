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
