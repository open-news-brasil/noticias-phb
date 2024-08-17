from thefuzz.fuzz import partial_ratio
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from noticias_phb.items import NewsItem
from noticias_phb.pipelines import BaseNewsPipeline


class DuplicatedItemsPipeline(BaseNewsPipeline):
    items: list[ItemAdapter] = []

    def has_equivalent_title(self, title: str) -> bool:
        for scrapped in self.current_scrapped_titles:
            if partial_ratio(title.lower(), scrapped) >= 80:
                return True
        for item in self.items:
            if partial_ratio(title.lower(), item.get("title", "").lower()) >= 70:
                return True
        return False

    def process_item(self, item: NewsItem, spider) -> NewsItem:
        adapter = ItemAdapter(item)
        link = adapter.get("link")
        title = adapter.get("title")
        if link in self.current_scrapped_links:
            raise DropItem(item)
        elif self.has_equivalent_title(title):
            raise DropItem(item)
        self.items.append(item)
        return item