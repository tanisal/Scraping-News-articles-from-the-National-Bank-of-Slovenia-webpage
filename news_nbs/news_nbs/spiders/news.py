import scrapy
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from news_nbs.items import NewsNbsItem
from unidecode import unidecode

class NewsSpider(scrapy.Spider):
    name = 'news'
    item = NewsNbsItem()
    start_urls = [  # "https://nbs.sk/wp-json/nbs/v1/post/list",
        "file:///C:/git/Scrapy/news_nbs/api_response.html"
    ]

    # def parse(self, response):
    #     sel = Selector(response)
    #     articles = sel.css("div.archive-results > a.archive-results__item")
    #     for article in articles:
            
    #         loader = ItemLoader(item=NewsNbsItem(), selector=article)

    #         loader.add_css("date", "div.date::text")
    #         loader.add_css("labels", "div.label::text")
    #         loader.add_css("name", "h2.h3::text")
    #         loader.add_css("link", "a::attr(href)")
    #         links = response.css("a::attr(href)")
    #         yield loader.load_item()
    #     for a in links:
    #         print(a)
    #         yield response.follow(a, callback=self.parse_content, meta={"item": loader.load_item()})
         

    # def parse_content(self, response):
    #     # print(response.meta['item'])
    #     selector = Selector(response=response)# type='html')
    #     loader = ItemLoader(item=response.meta["item"],selector=selector)
    #     #loader.add_css("content", "div.section > p")
    #     #loader.add_css("content","div.nbs-content")
        
    #     yield loader.load_item()




    def parse(self, response):
        sel = Selector(response)
        articles = sel.css("div.archive-results > a.archive-results__item")
        for article in articles:
            
            item=NewsNbsItem()
            item["date"] = article.css("div.date::text").get()
            item["labels"] = article.css("div.label::text").getall()
            item["name"] = unidecode(article.css("h2.h3::text").get())
            item["link"] = article.css("a::attr(href)").get()

            links = article.css("a::attr(href)")
            
            for a in links:
                print(a)
                yield response.follow(a, callback=self.parse_content, meta={"item": item})



    def parse_content(self,response):
        item = response.meta["item"]
        try:
            step1 = response.xpath("//p").getall()
            step2 = " ".join(step1).split('<p style="font-size:14px">')[0]
            step3 = step2.replace("\n", "")
            step4 = BeautifulSoup(step3, "lxml").get_text().strip()

            item["content"] = [unidecode(step4)]
        except:
            item["content"] = "Nothing for now"
        yield item





#  '''
#             item = NewsNbsItem()
#             item["date"] = article.css("div.date::text").get()
#             item["labels"] = article.css("div.label::text").get()
#             item["name"] = article.css("h2.h3::text").get()
#             yield item
#             links = response.css("a::attr(href)").get()
#             for a in links:
#                 yield response.follow(
#                     a, callback=self.parse_content, meta={"item": item})
# '''

    
#     '''
#     #     item = response.meta["item"]
#     #     try:
#     #         step1 = response.xpath("//p").getall()
#     #         step2 = " ".join(step1).split('<p style="font-size:14px">')[0]
#     #         step3 = step2.replace("\n", "")
#     #         step4 = BeautifulSoup(step3, "lxml").get_text().strip()
#     #         item["content"] = [step4]
#     #     except:
#     #         item["content"] = "Nothing for now"
#     #     yield item

# '''
