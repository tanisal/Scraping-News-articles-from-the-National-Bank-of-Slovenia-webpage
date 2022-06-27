import scrapy
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from news_nbs.items import NewsNbsItem
from unidecode import unidecode
import json

class NewsSpider(scrapy.Spider):
    name = 'news'
    
    start_urls = [ "https://nbs.sk/en/press/news-overview/"]

    headers = {
    'Accept': 'application/json, */*;q=0.1',
    'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Cookie': 'cookie_cnsnt=required%2Canalytics; _gid=GA1.2.1716664283.1655990651; pll_language=en; _ga=GA1.1.1842644514.1655990645; _ga_M9SPDPXFS5=GS1.1.1656318220.30.0.1656318231.0',
    'DNT': '1',
    'Origin': 'https://nbs.sk',
    'Pragma': 'no-cache',
    'Referer': 'https://nbs.sk/en/press/news-overview/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'X-WP-Nonce': '135f09d07e',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    }

    payload = json.dumps({
    'gbConfig': {
        'limit': 20,
        'categories': [
            32424,
            32416,
            8,
            32418,
            32420,
        ],
        'className': '',
        'template': 'links',
        'tags': [],
    },
    'lang': 'en',
    'limit': 20,
    'offset': 0,
    'filter': {
        'lang': 'en',
    },
    'onlyData': False,
    })


    def start_requests(self):
        urls = "https://nbs.sk/wp-json/nbs/v1/post/list?_locale=user"

        yield scrapy.Request(
            url=urls,
            method="POST",
            headers=self.headers,
            body=self.payload,
            callback=self.parse,
        )
 
    def parse(self, response):
        res = json.loads(response.body)['html']
        sel = Selector(text=res)
        
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
            item["content"] = "Not a valid news content"
        yield item

