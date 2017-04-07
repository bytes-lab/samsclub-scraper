# -*- coding: utf-8 -*-
import re
import os
import django
import scrapy
import requests
import json
import datetime
from os import sys, path
from selenium import webdriver
from scrapy.selector import Selector

from ..tasks import store_product

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "samsclub_site.settings")
django.setup()

from product.models import *
from product.views import *

class SamsclubSpider(scrapy.Spider):
    name = "samsclub"

    header = {
        "User-Agent": "samsclub_scraper (+http://www.yourdomain.com)"
    }

    def __init__(self, task_id, mode=0, categories=[], products=[]):
        self.task_id = int(task_id)
        self.mode = int(mode)
        self.categories = categories
        self.excludes = []        
        self.products = products

        if mode == 0:
            self.categories = get_subcategories()
            self.excludes = [item.url for item in Product.objects.all()]
        elif mode == 1:
            set_old_category_products(self.categories[0])            
            self.excludes = get_category_products(self.categories[0])
        elif mode == 2:
            products = products.replace('\n', ',')
            products_ = [int(item) for item in products.split(',')]
            self.products = Product.objects.filter(id__in=products_)

    def start_requests(self):
        if self.mode in [0, 1]:
            return [scrapy.Request('https://www.samsclub.com{}.cp'.format(item), 
                                   headers=self.header, 
                                   callback=self.parse) 
                    for item in self.categories]
        else:
            product_requests = []
            for product in self.products:
                request = scrapy.Request(product.url, 
                                         headers=self.header, 
                                         callback=self.detail)
                request.meta['model_num'] = product.special
                request.meta['category'] = product.category
                product_requests.append(request)
            return product_requests

    def closed(self, reason):
        self.update_run_time()

    def parse(self, response):
        if self.stop_scrapy():
            return

        cates = response.css('ul.catLeftNav li a::attr(href)').extract()
        cates = [item.split('.cp')[0] for item in cates]
        products = response.css('div.sc-product-card')

        if cates:
            for url in cates:
                url_ = 'https://www.samsclub.com{}.cp'.format(url)
                yield scrapy.Request(url_, headers=self.header, callback=self.parse)
        elif products:
            for product in products:
                detail_link = 'https://www.samsclub.com' + product.css('a.cardProdLink::attr(href)').extract_first()
                detail_link = detail_link.split('?')[0]

                if not detail_link in self.excludes:
                    model_num = product.css('span.list-view-modelnumber::text').extract_first()

                    request = scrapy.Request(detail_link, headers=self.header, callback=self.detail)
                    request.meta['model_num'] = model_num
                    request.meta['category'] = response.url.split('.cp')[0][24:]
                    yield request

            # for other pages / pagination
            offset = response.meta.get('offset', 0)
            total_records = response.meta.get('total_records', self.get_total_records(response))
            
            if offset + 48 < total_records:
                base_url = response.url.split('?')[0]
                next_url = base_url+'?offset={}'.format(offset)
                request = scrapy.Request(next_url, headers=self.header, callback=self.parse)
                request.meta['offset'] = offset + 48
                request.meta['total_records'] = total_records
                yield request


    def detail(self, response):
        if self.stop_scrapy():
            return

        sel = Selector(response)
        item_id = response.css('input[id=mbxProductId]::attr(value)').extract_first()
        sku_id = response.css('input[id=pSkuId]::attr(value)').extract_first()
        price = response.css('span[itemprop=price]::text').extract_first() or 0
        old_price = response.css('span.strikedPrice::text').extract_first()
        promo = self.get_promo(price, old_price)
        picture = response.css('img[itemprop=image]::attr(src)').extract_first()
        title = response.css('img[itemprop=image]::attr(title)').extract_first()
        detail_info = self.get_detail(item_id)
        base_url = response.url.split('?')[0]
        bullet_points = detail_info['Description'] or ''

        html_tags = ['<ul>', '</ul>', '<li>', '</li>', '<b>', '</b>', '<p>', '</p>', 
                     '<div>', '</div>']
        for htag in html_tags:
            bullet_points = bullet_points.replace(htag, '')

        rating = detail_info['FilteredReviewStatistics']['AverageOverallRating']
        rating = '{0:0.1f}'.format(float(rating)) if rating else 0
        review_count = detail_info['FilteredReviewStatistics']['TotalReviewCount']

        if self.mode == 2:
            quantity = self.get_real_quantity(base_url, sku_id, item_id)
        else:
            quantity = 9999

        item = {
            'id': response.css('input[id=itemNo]::attr(value)').extract_first(),
            'title': title,
            'price': '$'+price if price else 0,
            'picture': picture,
            'rating': rating or 0,
            'review_count': review_count,
            'delivery_time': response.css('div.finePrint::text').extract_first().replace(u'\u2019', '\''),
            'bullet_points': bullet_points,
            'details': response.css('div.freeDelvryTxt::text').extract_first(),
            'promo': promo,
            'special': response.meta['model_num'].replace(u'\xa0',''),
            'quantity': quantity,
            'min_quantity': 1,
            'category_id': response.meta['category'],
            'url': base_url
        }        
        store_product.apply_async((item,))
        yield item

    def get_real_quantity(self, referer, sku_id, product_id):
        url = 'https://www.samsclub.com/sams/shop/product.jsp?productId={}&_DARGS=/sams/shop/product/moneybox/moneyBoxButtons.jsp'.format(product_id)
        header = {
            'Host': 'www.samsclub.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': referer,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive'
        }

        body = "/sams_dyncharset=UTF-8&_dynSessConf=-8663347360612715418&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.continueShoppingURL=%2Fsams%2Fshop%2Fproduct.jsp%3FproductId%3D==PRODUCT==&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.continueShoppingURL=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.addMultipleItemsToOrderSuccessURL=%2Fsams%2Fcart%2FaddToCartConfirmPage.jsp&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.addMultipleItemsToOrderSuccessURL=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.fromProductDetailPage=true&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.fromProductDetailPage=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.fromStore=true&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.fromStore=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.baseProductId===PRODUCT==&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.baseProductId=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.addMultipleItemsToOrderErrorURL=%2F&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.addMultipleItemsToOrderErrorURL=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.productIds===PRODUCT==&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.productIds=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.catalogRefIds===SKU==&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.catalogRefIds=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.deliveryQuantitiesMap.0=9999&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.deliveryQuantitiesMap.0=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.pickUpQuantitiesMap.0=0&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.pickUpQuantitiesMap.0=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.frequency=&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.frequency=+&%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.samsAddItemToCart=submit&_D%3A%2Fatg%2Fcommerce%2Forder%2Fpurchase%2FCartModifierFormHandler.samsAddItemToCart=+&_DARGS=%2Fsams%2Fshop%2Fproduct%2Fmoneybox%2FmoneyBoxButtons.jsp".replace('==SKU==', sku_id).replace('==PRODUCT==', product_id)

        quantity = '9999'

        try:
            res = requests.post(url=url, headers=header, data=body)
        except Exception, e:
            pass

        try:
            driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true',
                                                       '--ssl-protocol=any',
                                                       '--load-images=false'])
            for item in res.headers['Set-Cookie'].split(', '):
                for item_ in item.split(';'):
                    try:
                        idx = item_.index('=')
                        name = item_[:idx].strip()
                        value = item_[idx+1:]
                        if name.lower() not in ['path', 'domain', 'expires']:
                            cook = {u'domain': u'www.samsclub.com', u'name': name, u'value': value, u'path': u'/'}
                            driver.add_cookie(cook)
                    except Exception, e:
                        pass
            driver.get('https://www.samsclub.com/sams/cart/cart.jsp?xid=hdr_cart_view-cart-and-checkout')
            checkout=driver.find_element_by_id('none')
            driver.implicitly_wait(25)
            checkout.click()
            quantity=driver.find_element_by_id('orderCount').text
            driver.quit()
        except Exception, e:
            pass

        return int(quantity)

    def get_total_records(self, response):
        total_records = re.search(r'\s\'totalRecords\':\'(\d+?)\',\s*', response.body)
        return int(total_records.group(1))

    def get_promo(self, price, old_price):
        # return old_price
        if old_price:
            old_price = re.search(r'^\D+([\d\.]+?)$', old_price)
            if old_price:
                old_price = old_price.group(1)
                discount = float(old_price) - float(price)            
                return '${0:0.1f} off'.format(discount)

    def get_detail(self, product_id):
        url = 'https://api.bazaarvoice.com/data/batch.json?passkey=dap59bp2pkhr7ccd1hv23n39x&apiversion=5.5&displaycode=1337-en_us&resource.q0=products&filter.q0=id%3Aeq%3A==**==&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen_US&filter_answers.q0=contentlocale%3Aeq%3Aen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&resource.q1=questions&filter.q1=productid%3Aeq%3A==**==&filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=totalanswercount%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen_US&filter_answers.q1=contentlocale%3Aeq%3Aen_US&sort_answers.q1=totalpositivefeedbackcount%3Adesc%2Ctotalnegativefeedbackcount%3Aasc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3A==**==&filter.q2=contentlocale%3Aeq%3Aen_US&sort.q2=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen_US&filter_comments.q2=contentlocale%3Aeq%3Aen_US&limit.q2=8&offset.q2=0&limit_comments.q2=3&resource.q3=reviews&filter.q3=productid%3Aeq%3A==**==&filter.q3=contentlocale%3Aeq%3Aen_US&limit.q3=1&resource.q4=reviews&filter.q4=productid%3Aeq%3A==**==&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=issyndicated%3Aeq%3Afalse&filter.q4=rating%3Agt%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Aen_US&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts&filter_reviews.q4=contentlocale%3Aeq%3Aen_US&limit.q4=1&resource.q5=reviews&filter.q5=productid%3Aeq%3A==**==&filter.q5=isratingsonly%3Aeq%3Afalse&filter.q5=issyndicated%3Aeq%3Afalse&filter.q5=rating%3Alte%3A3&filter.q5=totalpositivefeedbackcount%3Agte%3A3&filter.q5=contentlocale%3Aeq%3Aen_US&sort.q5=totalpositivefeedbackcount%3Adesc&include.q5=authors%2Creviews%2Cproducts&filter_reviews.q5=contentlocale%3Aeq%3Aen_US&limit.q5=1&callback=BV._internal.dataHandler0'
        url = url.replace('==**==', product_id)

        try:
            res = requests.get(url=url)
            quantity_ = json.loads(res.text[26:-1])['BatchedResults']['q0']['Results'][0]
        except Exception, e:
            print '=============================='
            quantity_ = {
                'Description': '',
                'FilteredReviewStatistics': {
                    'AverageOverallRating': '',
                    'TotalReviewCount': ''
                } 
            }

        return quantity_

    def update_run_time(self):
        if self.task_id:
            task = ScrapyTask.objects.get(id=self.task_id)
            task.last_run = datetime.datetime.now()
            task.status = 2 if task.mode == 2 else 0       # Sleeping / Finished
            task.update()

    def stop_scrapy(self):
        if self.task_id:
            st = ScrapyTask.objects.filter(id=self.task_id).first()
            return not st or st.status == 3
