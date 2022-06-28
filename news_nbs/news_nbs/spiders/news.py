import scrapy
from bs4 import BeautifulSoup
from scrapy.selector import Selector
from news_nbs.items import NewsNbsItem
from unidecode import unidecode
import json

class NewsSpider(scrapy.Spider):
    #NAme of the spider
    name = 'news'
    #Main url which we will scrape
    start_urls = [ "https://nbs.sk/en/press/news-overview/"]
    #Headers for the request
    headers = {  
    'Accept': 'application/json, */*;q=0.1', 
    'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
    'Cache-Control': 'no-cache' ,
    'Connection': 'keep-alive' ,
    'Content-Type': 'application/json' ,
    'Cookie': 'cookie_cnsnt=required%2Canalytics; _gid=GA1.2.1716664283.1655990651; pll_language=en; _ga=GA1.1.1842644514.1655990645; _ga_M9SPDPXFS5=GS1.1.1656397592.34.0.1656397600.0' ,
    'DNT':'1' ,
    'Origin': 'https://nbs.sk' ,
    'Pragma': 'no-cache' ,
    'Referer': 'https://nbs.sk/en/press/news-overview/' ,
    'Sec-Fetch-Dest': 'empty' ,
    'Sec-Fetch-Mode': 'cors' ,
    'Sec-Fetch-Site': 'same-origin' ,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36' ,
    'X-WP-Nonce': 'a3ba779f9e' ,
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"' ,
    'sec-ch-ua-mobile': '?0' ,
    'sec-ch-ua-platform': '"Windows"'

    }
    #Payload for the request post method, which we need in order to receive info back 
    #For the limit in the json file i put 20, for 20 articles new need
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

    # Request post function, giving us back as response a json file
    def start_requests(self):
        urls = "https://nbs.sk/wp-json/nbs/v1/post/list?_locale=user"

        yield scrapy.Request(
            url=urls,
            method="POST",
            headers=self.headers,
            body=self.payload,
            callback=self.parse,
        )
    #First parse functions, with which we grab the html from the json file from the response
    def parse(self, response):
        #taking the html part we need
        res = json.loads(response.body)['html']
        #converting it to slector object, that we need after
        sel = Selector(text=res)
        
        #looping through all the articles info on the page and saving it in a item
        articles = sel.css("div.archive-results > a.archive-results__item")
        for article in articles:
            #creating item instance
            item=NewsNbsItem()
            #adding needed info
            item["date"] = article.css("div.date::text").get()
            item["labels"] = article.css("div.label::text").getall()
            item["name"] = unidecode(article.css("h2.h3::text").get())
            item["link"] = article.css("a::attr(href)").get()
            #Taking all the links of the articles, and looping through them
            links = article.css("a::attr(href)")
            for a in links:
                #sending one by one the link to the next parse function for second level scraping
                yield response.follow(a, callback=self.parse_content, meta={"item": item},dont_filter = True)


    #Second level parse function, to grab the content of the individual news
    def parse_content(self,response):
        
        #transfering the meta of item saved in the first level above
        item = response.meta["item"]
        try:
            #In order to take the news content from the different website with different 
            #structures i took a wider scraping aproach, taking all the paragraph raw info
            step1 = response.xpath("//p").getall()
            #cleaning the data
            step2 = " ".join(step1).split('<p style="font-size:14px">')[0]
            #further cleaning
            step3 = step2.replace("\n", "")
            #removing the html tags/ bs4 wors better here that w3lib.html
            step4 = BeautifulSoup(step3, "lxml").get_text().strip()
            #saving the content, clening the unicode giberish
            item["content"] = [unidecode(step4)]
        except:
            #if i don find a website with paragpahs , then receiving exeption
            item["content"] = "Not a valid news content"
        #returning all the collected data from level one and two
        yield item

