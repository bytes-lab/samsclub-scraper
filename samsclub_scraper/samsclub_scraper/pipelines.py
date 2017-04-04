from tasks import store_product

class SamsclubScraperPipeline(object):
    def open_spider(self, spider):
        print spider.mode, '@@@@@@@@@@'

    def process_item(self, item, spider):
        print '###################'
        store_product.apply_async(kwargs={'item': item})
        return item

    def close_spider(self, spider):
        spider.update_run_time()
