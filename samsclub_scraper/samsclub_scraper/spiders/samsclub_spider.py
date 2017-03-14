import re
import scrapy
import requests
import json

from scrapy.selector import Selector


class SamsclubSpider(scrapy.Spider):
    name = "samsclub"

    header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }

    def __init__(self, param=[]):
        self.param = param

    def start_requests(self):
        categories = [
            # 'spring-renewal/5160101',
            'fine-writing-supplies/9165'
        ]
        return [scrapy.Request('https://www.samsclub.com/sams/{}.cp'.format(item), headers=self.header, callback=self.parse) for item in categories]

    def parse(self, response):
        products = response.css('div.sc-product-card')

        if products:
            for product in products:
                title = product.css('figcaption.sc-text-body::text').extract_first()
                model_num = product.css('span.list-view-modelnumber::text').extract_first()
                picture = product.css('img.cardProdImg::attr(data-src)').extract_first()
                detail_link = 'https://www.samsclub.com' + product.css('a.cardProdLink::attr(href)').extract_first()
                shipping = product.css('span.sc-free-shipping::text').extract_first()

                request = scrapy.Request(detail_link, headers=self.header, callback=self.detail)
                request.meta['title'] = title
                request.meta['model_num'] = model_num
                request.meta['picture'] = picture
                request.meta['shipping'] = shipping
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
        # else:
        #     for url in cates:
        #         yield scrapy.Request(url, headers=self.header, callback=self.parse)


    def detail(self, response):
        sel = Selector(response)
        item_id = response.css('input[id=mbxProductId]::attr(value)').extract_first()
        # price = re.search(r'\s*"item_price":"([\d\.]+?)",\s*', response.body).group(1)
        old_price = product.css('span.strikedPrice::text').extract_first()
        promo = self.get_promo(price, old_price)

        print item_id, '#######33'

        yield {
            'title': response.meta['title'],
            'id': response.css('input[id=itemNo]::attr(value)').extract_first(),
            'picture': response.meta['picture'],
            'price': response.css('span[itemprop=price]::text').extract_first(),
            'model_num': response.meta['model_num'],
            # 'promo': response.meta['promo'],
            'shipping': response.meta['shipping'],
            'delivery_time': response.css('div.finePrint::text').extract_first(),
        }        

    def get_description(self, des_key, des_val):
        description = ''
        if des_key:
            des_val = [item.strip() for item in des_val if item.strip()]
            for idx in range(len(des_val)):
                description += '{} {}\n'.format(des_key[idx].strip().encode('utf-8'), 
                                                des_val[idx].strip().encode('utf-8'))
        return description.replace(',', '')

    def get_real_quantity(self, body):
        url = 'https://www.costco.com/AjaxManageShoppingCartCmd'
        header = {
            'Accept':'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.8',
            'Connection':'keep-alive',
            'Content-Length':'334',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie':'spid=BB039764-30D4-488E-A2DA-3416AB5F90D4; s=undefined; hl_p=ae4eb09f-121c-45cf-a807-78a231307294; WC_SESSION_ESTABLISHED=true; WC_ACTIVEPOINTER=%2d1%2c10301; BVImplmain_site=2070; BVBRANDID=9c062aa4-9478-4cc7-8684-f1c52f41118b; AMCVS_97B21CFE5329614E0A490D45%40AdobeOrg=1; WC_PERSISTENT=1BGhult3vWEtlQhpFPW%2fYyGLB%2f8%3d%0a%3b2017%2d03%2d02+07%3a59%3a56%2e301%5f1487263129490%2d838314%5f10301%5f308580336%2c%2d1%2cUSD%5f10301; WC_USERACTIVITY_308580336=308580336%2c10301%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2cnull%2cNPXKfRraLy80H%2facJBFuHUYe3X6iYFGrmBkLoO8pkRG%2fOKYM0Ow8VkcWzCfYx3%2bjEAxPYsnEhIvv%0aI322SzD41rPlK4uX0SGC1rkdkBuu9JeakMfDdJAgGEeK2LE%2fyrt2aTbJUxqqvmaAn0Xzt3aMHf%2b2%0aY0ZUSc2fxbvQDhb3B%2fsevHlNC4Gi8wDnS%2fIntMBnskY%2bRs1g%2btevRm2Lw5k0Fw%3d%3d; BVBRANDSID=cafd4e57-a4aa-47ec-a502-9c0a0b82318d; rr_rcs=eF4NxrENgDAMBMAmFbs8yju2E2_AGkkQEgUdMD9cdSk9cxvTKqN3WDOBuhB5FP1nHjzoecpyvfe5r0KC2ppWD8shFSEAP2Y1EJs; cartCountCookie=1; lastAddedProductId=169831; s_sq=%5B%5BB%5D%5D; C_CLIENT_SESSION_ID=c1672e8d-e50c-4830-862f-007dbffa13f5; WC_AUTHENTICATION_308580336=308580336%2cerDLv1iRML0kyZxjQKZ7DFQJnno%3d; JSESSIONID=0000AkynmIuDDqCCUolR-UPdrns:163c2eho3; ak_bmsc=5BF67D91DB9A91E1ED5BFFF822ECFF3917C663CF22580000095CB85822E90155~pl5UxYn+5vCqxw2Jd99L1zXHJyj3xUPoeqyk74K1w/HJlcCh3okhDXLL1qHo//44Y1pacZ5iTLrzfDpXpL8+RVq2PiRULQ0Xd+KgQ9ddWhr/MZjcx2Z14dUcxJE3VqOTVDRS7ZzDTapWJxcgG+oaPE9cMs9XtNPc+zcct1iunG/tvDwFO63ibb+skGm8hLaqJ0gW43h8VFh+K3sWiApRspwQ==; sp_ssid=1488477229844; WRUIDAWS=1120658076230015; __CT_Data=gpv=58&apv_59_www33=58&cpv_59_www33=58&rpv_59_www33=58; AMCV_97B21CFE5329614E0A490D45%40AdobeOrg=-1330315163%7CMCIDTS%7C17228%7CMCMID%7C14749491232221946818716045741455311554%7CMCAID%7CNONE%7CMCOPTOUT-1488484459s%7CNONE; s_cc=true',
            'DNT':'1',
            'Host':'www.costco.com',
            'Origin':'https://www.costco.com',
            'Referer':'https://www.costco.com/Round-Brilliant-3.00-ctw-VS2-Clarity%2c-I-Color-Diamond-Platinum-Three-Stone-Ring.product.11043679.html',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest'        
        }

        res = requests.post(url=url, headers=header, data=body)
        try:
            quantity_ = res.json()['orderErrMsgObj']['1']
        except Exception, e:
            print '==============================', res.json()
            if 'errorMessage' in res.json():
                return 0
            return '9999'       # orderErrMsgObj
        quantity = re.search(r'\s*only (.+?) are\s*', quantity_)
        return quantity.group(1) if quantity else '9999'

    def get_total_records(self, response):
        total_records = re.search(r'\s\'totalRecords\':\'(\d+?)\',\s*', response.body)
        return int(total_records.group(1))

    def get_promo(self, price, old_price):
        # return old_price
        if old_price:
            old_price = re.search(r'^\D+([\d\.]+?)$', old_price)
            old_price = old_price.group(1)
            return float(old_price) - float(price)

