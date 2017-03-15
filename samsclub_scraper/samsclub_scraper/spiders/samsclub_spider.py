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
            # 'office-supplies/1706'
        ]
        return [scrapy.Request('https://www.samsclub.com/sams/{}.cp'.format(item), headers=self.header, callback=self.parse) for item in categories]

    def parse(self, response):
        cates = response.css('ul.catLeftNav li a::attr(href)').extract()
        cates = [item.split('.cp')[0] for item in cates]
        products = response.css('div.sc-product-card')

        if cates:
            for url in cates:
                url_ = 'https://www.samsclub.com{}.cp'.format(url)
                yield scrapy.Request(url_, headers=self.header, callback=self.parse)
        elif products:
            for product in products:
                # model_num = product.css('span.list-view-modelnumber::text').extract_first()
                detail_link = 'https://www.samsclub.com' + product.css('a.cardProdLink::attr(href)').extract_first()

                request = scrapy.Request(detail_link, headers=self.header, callback=self.detail)
                # request.meta['model_num'] = model_num
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
        sel = Selector(response)
        item_id = response.css('input[id=mbxProductId]::attr(value)').extract_first()
        price = response.css('span[itemprop=price]::text').extract_first()
        old_price = response.css('span.strikedPrice::text').extract_first()
        promo = self.get_promo(price, old_price)
        picture = response.css('img[itemprop=image]::attr(src)').extract_first()
        title = response.css('img[itemprop=image]::attr(title)').extract_first()
        detail_info = self.get_detail(item_id)
        bullet_points = detail_info['Description'].replace('<ul>', '').replace('</ul>', '').replace('<li>', '').replace('</li>', '')
        rating = detail_info['FilteredReviewStatistics']['AverageOverallRating']
        review_count = detail_info['FilteredReviewStatistics']['TotalReviewCount']

        yield {
            'title': title,
            'id': response.css('input[id=itemNo]::attr(value)').extract_first(),
            'picture': picture,
            'price': price,
            'bullet_points': bullet_points,
            'rating': rating,
            'review_count': review_count,
            # 'model_num': response.meta['model_num'],
            'promo': promo,
            'shipping': response.css('div.freeDelvryTxt::text').extract_first(),
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

    def get_detail(self, product_id):
        url = 'https://api.bazaarvoice.com/data/batch.json?passkey=dap59bp2pkhr7ccd1hv23n39x&apiversion=5.5&displaycode=1337-en_us&resource.q0=products&filter.q0=id%3Aeq%3A==**==&stats.q0=questions%2Creviews&filteredstats.q0=questions%2Creviews&filter_questions.q0=contentlocale%3Aeq%3Aen_US&filter_answers.q0=contentlocale%3Aeq%3Aen_US&filter_reviews.q0=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen_US&resource.q1=questions&filter.q1=productid%3Aeq%3A==**==&filter.q1=contentlocale%3Aeq%3Aen_US&sort.q1=totalanswercount%3Adesc&stats.q1=questions&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers&filter_questions.q1=contentlocale%3Aeq%3Aen_US&filter_answers.q1=contentlocale%3Aeq%3Aen_US&sort_answers.q1=totalpositivefeedbackcount%3Adesc%2Ctotalnegativefeedbackcount%3Aasc&limit.q1=10&offset.q1=0&limit_answers.q1=10&resource.q2=reviews&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3A==**==&filter.q2=contentlocale%3Aeq%3Aen_US&sort.q2=helpfulness%3Adesc%2Ctotalpositivefeedbackcount%3Adesc&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments&filter_reviews.q2=contentlocale%3Aeq%3Aen_US&filter_reviewcomments.q2=contentlocale%3Aeq%3Aen_US&filter_comments.q2=contentlocale%3Aeq%3Aen_US&limit.q2=8&offset.q2=0&limit_comments.q2=3&resource.q3=reviews&filter.q3=productid%3Aeq%3A==**==&filter.q3=contentlocale%3Aeq%3Aen_US&limit.q3=1&resource.q4=reviews&filter.q4=productid%3Aeq%3A==**==&filter.q4=isratingsonly%3Aeq%3Afalse&filter.q4=issyndicated%3Aeq%3Afalse&filter.q4=rating%3Agt%3A3&filter.q4=totalpositivefeedbackcount%3Agte%3A3&filter.q4=contentlocale%3Aeq%3Aen_US&sort.q4=totalpositivefeedbackcount%3Adesc&include.q4=authors%2Creviews%2Cproducts&filter_reviews.q4=contentlocale%3Aeq%3Aen_US&limit.q4=1&resource.q5=reviews&filter.q5=productid%3Aeq%3A==**==&filter.q5=isratingsonly%3Aeq%3Afalse&filter.q5=issyndicated%3Aeq%3Afalse&filter.q5=rating%3Alte%3A3&filter.q5=totalpositivefeedbackcount%3Agte%3A3&filter.q5=contentlocale%3Aeq%3Aen_US&sort.q5=totalpositivefeedbackcount%3Adesc&include.q5=authors%2Creviews%2Cproducts&filter_reviews.q5=contentlocale%3Aeq%3Aen_US&limit.q5=1&callback=BV._internal.dataHandler0'
        url = url.replace('==**==', product_id)
        res = requests.get(url=url)

        try:
            quantity_ = json.loads(res.text[26:-1])['BatchedResults']['q0']['Results'][0]
        except Exception, e:
            print '==============================', res.json()
            if 'errorMessage' in res.json():
                return 0
        return quantity_