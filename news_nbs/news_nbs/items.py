# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from bs4 import BeautifulSoup
import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from unidecode import unidecode
from w3lib.html import remove_tags

def separate(text):
    result= " ".join(text).split('<p style="font-size:14px">')[0]
    return result

def tags(text):
    return BeautifulSoup(text,"lxml").get_text()

class NewsNbsItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    labels = scrapy.Field()
    content = scrapy.Field(
        input_processor=MapCompose(remove_tags),
        # output_processor=TakeFirst()

    )
         
        
