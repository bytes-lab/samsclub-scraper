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

    header = {
        'Host': 'www.costco.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.costco.com/',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
        'Cookie': 'hl_p=2afe8118-2ddc-4668-a5f5-69ecb4e174b4; AMCVS_97B21CFE5329614E0A490D45%40AdobeOrg=1; AMCV_97B21CFE5329614E0A490D45%40AdobeOrg=-1330315163%7CMCIDTS%7C17225%7CMCMID%7C46504056737436331013923092520674821883%7CMCAAMLH-1488841099%7C7%7CMCAAMB-1488841099%7CcIBAx_aQzFEHcPoEv0GwcQ%7CMCOPTOUT-1488243499s%7CNONE%7CMCAID%7CNONE; spid=41696B99-29B7-4AD4-9931-B82044AB8A5F; s=undefined; WC_SESSION_ESTABLISHED=true; WC_PERSISTENT=ZzphjJ5imwc2khIEaUZZv0GHfmo%3d%0a%3b2017%2d02%2d27+15%3a02%3a09%2e872%5f1488236522430%2d140425%5f10301%5f%2d1002%2c%2d1%2cUSD%5f10301; WC_ACTIVEPOINTER=%2d1%2c10301; WC_USERACTIVITY_-1002=%2d1002%2c10301%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2chAev4P5zVpKYL3uQt4tYs30fIWMchuamGtyK1WNYKb2jYMWZGJ9H7STR3Y2NkIUcfEOR8AMfM6qq%0aZw8qbZRzSHUgbTDoYoVDUTvJ7HiJHuTm3sISf%2fSwjEviTrOCorTrAYHtSGojI5wQ%2fGDQ7WHFXpeq%0aaS1IumBdtU2Zy9mOvHovP3g%2fURy3YoeNgq3cxb1ODQW11DsPxrdzc0JoVchRMg%3d%3d; WC_GENERIC_ACTIVITYDATA=[4998293655%3atrue%3afalse%3a0%3a1dcjlbTjxYw009tqNW4xMIU9ltI%3d][com.ibm.commerce.context.audit.AuditContext|1488236522430%2d140425][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][CTXSETNAME|Store][com.ibm.commerce.context.globalization.GlobalizationContext|%2d1%26USD%26%2d1%26USD][com.ibm.commerce.catalog.businesscontext.CatalogContext|10701%26null%26false%26false%26false][com.ibm.commerce.context.base.BaseContext|10301%26%2d1002%26%2d1002%26%2d1][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000001002%264000000000000001002%26null%26%2d2000%26null%26null%26null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null]; BVImplmain_site=2070; BVBRANDID=6aff88e1-f1c9-422b-8f03-313ffe200d13; BVBRANDSID=1b0695d7-c7ce-44ea-a769-8b481d79316a; C_CLIENT_SESSION_ID=11da9079-1d04-4210-b3ed-1b2eafc3d836; JSESSIONID=0000luqPhp9_HS7gq3P-MRwj2iF:175b17ndl; WC_AUTHENTICATION_-1002=%2d1002%2c5M9R2fZEDWOZ1d8MBwy40LOFIV0%3d; ak_bmsc=08A485079047F511CFFD694EDB36178ACDB1473DD56900000AAFB458C8FD7240~plUYMxh+v7XvPGbykquoO75LNkvWcN+wuNudPEDCpz9JLZXa6wVMaFo6NRvGRBrDne2FQIkprFb4GVcYkzfMNsj6A7OezPdlitVqG6ZooyhwI8YiDrMgv5f0tVvYXbjQy0UPA1e8eZbuPjXwsuzpU3oqYxJnJz5iKg60i2TZ0xE5abD+cr75/dtGOfcmOIJLnUsJffIP0Pzb+8oeZ536uK/g==; s_sq=%5B%5BB%5D%5D; s_cc=true; sp_ssid=1488237818564; rr_rcs=eF4FwbsNgDAMBcAmFbs8hO34twFrhIRIFHTA_NyV5f6ea6xMBKoRLB5sqQEzgMrbd7JsxxCFnVNQfSa6k6KmWtuceHb_AWW8EUU'
    }

    # header = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
    # }

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
