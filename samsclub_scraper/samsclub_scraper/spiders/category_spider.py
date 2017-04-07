# -*- coding: utf-8 -*-
import re
import os
import django
import scrapy
import json
import random
from os import sys, path
from selenium import webdriver
from scrapy.selector import Selector

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samsclub_site.settings")
django.setup()

from product.models import *
from product.views import *

class CategorySpider(scrapy.Spider):
    name = "samsclub_category"

    def __init__(self, param=[]):
        self.param = param
        self.categories = get_subcategories()
        self.proxy_pool = [
            '192.241.100.70',
            '23.229.82.16',
            '198.154.80.250',
            '198.154.80.52',
            '192.241.126.232',
            '198.20.162.240',
            '45.72.80.201',
            '23.254.80.190',
            '23.250.8.170',
            '23.229.17.126',
            '192.186.191.135',
            '138.128.31.45',
            '23.250.90.218',
            '192.241.95.159',
            '104.227.5.229',
            '198.20.183.12',
            '23.229.82.205',
            '192.241.95.208',
            '45.57.239.3',
            '23.229.95.146',
            '23.236.136.14',
            '107.152.225.185',
            '104.144.255.137',
            '45.57.239.217',
            '104.227.79.185',
            '138.128.31.203',
            '198.154.80.201',
            '104.227.152.113'
        ]

    def start_requests(self):
        cate_requests = []
        for item in self.categories:
            request = scrapy.Request('https://www.samsclub.com{}.cp'.format(item), 
                                     callback=self.parse)
            request.meta['category'] = item
            # request.meta['proxy'] = 'http://'+random.choice(self.proxy_pool)
            cate_requests.append(request)
        return cate_requests


    def parse(self, response):
        cates = response.css('ul.catLeftNav li a::attr(href)').extract()
        cates_url = [item.split('.cp')[0] for item in cates]
        cates_title = response.css('ul.catLeftNav li a::text').extract()

        if cates:
            parent = response.meta['category']
            for item in zip(cates_url, cates_title):
                create_category(parent=parent, url=item[0], title=item[1])
                url_ = 'https://www.samsclub.com{}.cp'.format(item[0])
                request = scrapy.Request(url_, callback=self.parse)
                request.meta['category'] = item[0]
                # request.meta['proxy'] = 'http://'+random.choice(self.proxy_pool)
                yield request
