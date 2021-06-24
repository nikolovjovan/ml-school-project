from itemadapter import ItemAdapter

class TestPipeline:
    def process_item(self, item, spider):
        print()
        print(ItemAdapter(item))
        print()
        return item