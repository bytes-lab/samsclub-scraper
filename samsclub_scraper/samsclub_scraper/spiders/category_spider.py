# -*- coding: utf-8 -*-
import re
import os
import django
import scrapy
import requests
import json
from os import sys, path
from selenium import webdriver
from scrapy.selector import Selector

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samsclub_site.settings")
django.setup()

from product.models import *
from product.views import *

class SamsclubSpider(scrapy.Spider):
    name = "samsclub_category"

    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }

    def __init__(self, param=[]):
        self.param = param
        self.categories = get_subcategories('0000')

    def start_requests(self):
        for item in self.categories:
            request = scrapy.Request('https://www.samsclub.com/sams/{}.cp'.format(item), 
                                     headers=self.header, callback=self.parse)
            request.meta['category'] = item
            return request


    def parse(self, response):
        cates = response.css('ul.catLeftNav li a::attr(href)').extract()
        cates_url = [item.split('.cp')[0] for item in cates]
        cates_title = response.css('ul.catLeftNav li a::text').extract()

        if cates:
            upper_category = response.meta['category']
            for item in zip(cates_url, cates_title):
                save_category(parent_code=upper_category.code, url=item[0], title=item[1])
                url_ = 'https://www.samsclub.com{}.cp'.format(item[0])
                yield scrapy.Request(url_, headers=self.header, callback=self.parse)
