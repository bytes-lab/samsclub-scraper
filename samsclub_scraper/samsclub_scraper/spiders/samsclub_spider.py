import re
import scrapy
import requests
import json

from scrapy.selector import Selector


class SamsclubSpider(scrapy.Spider):
    name = "samsclub"

    header = {
        ':authority':'www.samsclub.com',
        ':method':'GET',
        ':path':'/sams/vacuum-cleaners/2780107.cp?navAction=pop',
        ':scheme':'https',
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding':'gzip, deflate, sdch, br',
        'accept-language':'en-US,en;q=0.8',
        'cache-control':'max-age=0',
        'cookie':'geoValidation=false; samsVisitor=5291470499; TBV=7; s_vi=[CS]v1|2C61779B8548B2A8-4000010420007024[CE]; __gads=ID=b4ba9f13b0147647:T=1489170233:S=ALNI_MaW3-xlHrWjYUvD6KnXL1o-vpOB_Q; AB_param=polaris; BVBRANDID=5f508bf6-7670-460c-a0c1-c1280229b76f; spid=3F3EC8CC-BA5D-48A6-9F68-1EE1BBC5A6B4; fsr.r=%7B%22d%22%3A90%2C%22i%22%3A%22d464c27-83421074-3d22-5b19-d566e%22%2C%22e%22%3A1489808364525%7D; optimizelyEndUserId=oeu1489207305794r0.347269585604594; optimizelySegments=%7B%223001840443%22%3A%22gc%22%2C%223008941363%22%3A%22direct%22%2C%223035770458%22%3A%22false%22%2C%223065020104%22%3A%22none%22%7D; optimizelyBuckets=%7B%7D; dcenv=TB-DAL; prftsekure=0; AMCVS_B98A1CFE53309C340A490D45%40AdobeOrg=1; s_tbm180=1; s_ev51=%5B%5B%27Internal%27%2C%271489380236604%27%5D%5D; productnum=34; inptime0_859_us=0; s=undefined; BVImplmain_site=1337; testVersion=versionA; s_stv=non-search; AMCV_B98A1CFE53309C340A490D45%40AdobeOrg=-1330315163%7CMCIDTS%7C17238%7CMCMID%7C19486871921550694101715393536039826814%7CMCAAMLH-1489811116%7C3%7CMCAAMB-1490018534%7CNRX38WO0n5BH8Th-nqAG_A%7CMCOPTOUT-1489420934s%7CNONE%7CMCAID%7C2C61779B8548B2A8-4000010420007024; SSID1=CABjFx1wAAAAAAAz78JYApuBHzPvwlgJAAAAAADfI6RaObvGWABjBkJiAAOHswsAM-_CWAkA_mcAAx52DAAz78JYCQAIZwADzVsMADPvwlgJAGplAAOBJgwAM-_CWAkA7mMAA5rsCwAz78JYCQARaQABtJQMADm7xlgBAKpSAAOopgoAM-_CWAkAAGgAAyF2DAAz78JYCQA; SSSC1=362.G6395937423670483714.9|21162.698024:25154.766855:25582.781466:25962.796289:26376.809933:26622.816670:26624.816673:26897.824500; samsHubbleSession=78E1D5ACBF7EC2301A973133295DECB6.estoreapp-44277895-2-70639384; SSRT1=DbzGWAAAAA; akavpau_P2=1489419878~id=241b528532e96ff76625ccc3cd315ba0; s_evar20=unidentified; s_evar58=5291470499; s_evar72=club-selected; prop_9=Not%20Logged%20In; evar_19=Not%20Logged%20In; s_sq=%5B%5BB%5D%5D; s_cc=true; _br_uid_2=uid%3D8944298102468%3Av%3D12.0%3Ats%3D1489170220352%3Ahc%3D97; fsr.s=%7B%22v%22%3A-1%2C%22rid%22%3A%22d464c27-83421074-3d22-5b19-d566e%22%2C%22ru%22%3A%22https%3A%2F%2Fwww.samsclub.com%2Fsams%2Fspring-renewal%2F5160101.cp%22%2C%22r%22%3A%22www.samsclub.com%22%2C%22st%22%3A%22%22%2C%22to%22%3A5%2C%22c%22%3A%22https%3A%2F%2Fwww.samsclub.com%2Fsams%2Fshark-rocket-dluxpro-hv325%2Fprod20201972.ip%22%2C%22pv%22%3A10%2C%22lc%22%3A%7B%22d1%22%3A%7B%22v%22%3A10%2C%22s%22%3Atrue%7D%7D%2C%22cd%22%3A1%2C%22cp%22%3A%7B%22s_eVar10%22%3A%22Repeat%22%2C%22s_pageName%22%3A%22pdp%3Ashark-rocket-deluxepro-upright-vacuum%22%2C%22s_channel%22%3A%22pdp%22%2C%22s_products%22%3A%22%3B103154%3B%3B%3B%3BeVarI%3D1%22%7D%2C%22f%22%3A1489419275072%2C%22sd%22%3A1%7D; SAT_RMEM=1; SAT_SRCH-IMP=0; SAT_POLARIS=2; SSLB=1; SSPV1=3oMAAAAAABsAEgAAAAAAAAAAAAEAAAAAAAA; NSC_JOxs2zfhe1jdcygeqrfzgndx0hpxlbc=ffffffff0949822445525d5f4f58455e445a4a4216cb; prftsl=0; JSESSIONID=78E1D5ACBF7EC2301A973133295DECB6.estoreapp-44277895-2-70639384; akavpau_P3=1489419882~id=03ed7a1709914cb05060b78baa6e04f1; BVBRANDSID=179bbed4-3002-4de5-a852-a54b8b5e0d56; s_cmdl=1; s_cm=undefinedInternalundefined; s_nr=1489419509213-Repeat; gpv_p6=cat%3Ahome%3Aappliances%3Avacuum-cleaners; s_ppvl=cat%253Ahome%253Aappliances%253Avacuum-cleaners%2C14%2C14%2C782%2C1536%2C482%2C1536%2C864%2C1.25%2CP; s_ppv=pdp%253Ashark-rocket-deluxepro-upright-vacuum%2C6%2C6%2C759%2C1536%2C759%2C1536%2C864%2C1.25%2CP',
        'referer':'https://www.samsclub.com/sams/dyson-ball-ttl-clean-upright-vacuum/prod17870042.ip?xid=plp5160101-spri:product:1:9',
        'upgrade-insecure-requests':1,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'    
    }

    def __init__(self, param=[]):
        self.param = param

    def start_requests(self):
        categories = [
            'spring-renewal/5160101'           
        ]

        return [scrapy.Request('https://www.samsclub.com/sams/{}.cp'.format(item), headers=self.header, callback=self.parse) for item in categories]

    def parse(self, response):
        products = response.css('div.sc-product-card ')
        cates = response.css('div.categoryclist div.col-md-3 a::attr(href)').extract()

        if products:
            for product in products:
                title = product.css('figcaption.sc-text-body::text').extract_first()
                id = product.css('span.list-view-itemnumber::text').extract_first()
                model_num = product.css('span.list-view-modelnumber::text').extract_first()
                price = product.css('span.hubbleTrackRecord::attr(data-price)').extract_first()

                yield {
                    'id': id,
                    'title': title,
                    'model_num': model_num,
                    'price': price
                }
                # if detail:
                #     request = scrapy.Request(detail, headers=self.header, callback=self.detail)
                #     request.meta['price'] = price
                #     request.meta['rating'] = rating
                #     request.meta['promo'] = promo
                #     request.meta['category'] = category
                #     request.meta['reviewCount'] = reviewCount
                #     yield request
        # else:
        #     for url in cates:
        #         yield scrapy.Request(url, headers=self.header, callback=self.parse)


    def detail(self, response):
        sel = Selector(response)
        pid = response.url[-14:-5]
        url = 'https://scontent.webcollage.net/costco/power-page?ird=true&channel-product-id=' + pid
       
        quantity = re.search(r'\s*"maxQty" : "(.+?)",',response.body)
        quantity = quantity.group(1) if quantity else '0'
        min_quantity = re.search(r'\s*"minQty" : "(.+?)",',response.body)
        min_quantity = min_quantity.group(1) if min_quantity else '0'

        if int(quantity) == 9999:
            quantity = self.get_real_quantity({
                'ajaxFlag': True,
                'actionType': sel.xpath("//input[@name='actionType']/@value").extract_first(),
                'backURL': sel.xpath("//input[@name='backURL']/@value").extract_first(),
                'catalogId': sel.xpath("//input[@name='catalogId']/@value").extract_first(),
                'langId': sel.xpath("//input[@name='langId']/@value").extract_first(),
                'storeId': sel.xpath("//input[@name='storeId']/@value").extract_first(),
                'authToken': sel.xpath("//input[@name='authToken']/@value").extract_first(),
                'productBeanId': sel.xpath("//input[@name='productBeanId']/@value").extract_first(),
                'categoryId': sel.xpath("//input[@name='categoryId']/@value").extract_first(),
                'catEntryId': sel.xpath("//input[@name='catEntryId']/@value").extract_first(),
                'addedItem': sel.xpath("//input[@name='addedItem']/@value").extract_first(),
                'catalogEntryId_1': sel.xpath("//input[@name='catEntryId']/@value").extract_first(),
                'quantity': 9999,
                'quantity_1': 9999
            })

        des_key = response.css('div.product-info-specs li span::text').extract()
        des_val = response.css('div.product-info-specs li::text').extract()
        description = self.get_description(des_key, des_val)
        special = sel.xpath("//div[@class='product-info-description']/div[contains(@style, 'text-align:center;')]/text()").extract_first()

        yield {
            'id': response.css('p.item-number span::attr(data-sku)').extract_first(),
            'title': response.css('h1::text').extract_first(),
            'price': response.meta['price'],
            'picture': sel.xpath("//img[@id='initialProductImage']/@src").extract_first(),
            'rating': response.meta['rating'],
            'review_count': response.meta['reviewCount'],
            'promo': response.meta['promo'],
            'category': response.meta['category'],
            'delivery_time': response.css('p.primary-clause::text').extract_first(),
            'bullet_points': '\n'.join(response.css('ul.pdp-features li::text').extract()),
            'details': description,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'special': special
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
