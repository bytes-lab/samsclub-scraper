# -*- coding: utf-8 -*-
import re
import os
import django
import scrapy
import json
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

    # header = {
    #     'Host': 'www.samsclub.com',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Cookie': 'SSLB=1; SSID1=CAA4Jx1iAAgAAABifMhYwI3BC2J8yFgLAAAAAADngcRaO03jWABjBgBoAAMidgwAYnzIWAsACGcAA89bDABifMhYCwCqUgADqKYKAGJ8yFgLAPxnAAMZdgwAO03jWAEAEWkAAbWUDAA7TeNYAQD-ZwADHnYMAGJ8yFgLAEJiAAOHswsAYnzIWAsAamUAAO5jAAA; SSRT1=O03jWAAAAA; SSPV1=DNsAAAAAABIAAgAAAAAAAAAAAAEAAAAAAAA; samsVisitor=5321890340; AMCV_B98A1CFE53309C340A490D45%40AdobeOrg=-1330315163%7CMCIDTS%7C17261%7CMCMID%7C27862484198763121203365960930288610703%7CMCAAMLH-1491896249%7C3%7CMCAAMB-1491896249%7CNRX38WO0n5BH8Th-nqAG_A%7CMCOPTOUT-1491298649s%7CNONE%7CMCAID%7C2C643E3305488618-40000104E00055FF; TBV=6; _br_uid_2=uid%3D7516093759295%3Av%3D12.0%3Ats%3D1489534053113%3Ahc%3D89; s_vi=[CS]v1|2C643E3305488618-40000104E00055FF[CE]; __gads=ID=6535f234e3c4e7ef:T=1489534055:S=ALNI_MbrP5G_hI7pmgNOAgV-nqDvNIuf2g; s_tbm180=1; s_ev51=%5B%5B%27Internal%27%2C%271489699487902%27%5D%5D; s_nr=1491291451726-Repeat; productnum=2; spid=3E683245-F94E-4D40-A845-211AA0785065; s=undefined; BVBRANDID=91d3f494-6093-447c-883e-94fec5e3ed3e; _abck=fnknhc13f0fdz1lgbfeh_1871; samsorder=8a715ae52d18516433ad551fdb14f4f5; AB_param=polaris',
    #     'Connection': 'keep-alive',
    #     'Upgrade-Insecure-Requests': '1'
    # }

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }

    def __init__(self, param=[]):
        self.param = param
        self.categories = get_subcategories()

    def start_requests(self):
        cate_requests = []
        for item in self.categories:
            request = scrapy.Request('https://www.samsclub.com{}.cp'.format(item), 
                                     headers=self.header, callback=self.parse)
            request.meta['category'] = item
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
                request = scrapy.Request(url_, headers=self.header, callback=self.parse)
                request.meta['category'] = item[0]
                yield request
