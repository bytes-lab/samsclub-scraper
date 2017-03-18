from tasks import store_product

class SamsclubScraperPipeline(object):
    def process_item(self, item, spider):
        store_product.apply_async(kwargs={'item': item})
        return item
