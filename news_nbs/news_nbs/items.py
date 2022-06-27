# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from bs4 import BeautifulSoup
from w3lib.html import remove_tags
from unidecode import unidecode

def remove_n(value):
    return value.replace("\n", "")

def bs_clean(value):
    return value.BeautifulSoup(value, "lxml").get_text().strip()

def separation(value):
    text = " ".join(value).split('<p style="font-size:14px">')[0]
    text = text.replace("\n", "")
    text =  BeautifulSoup(text, "lxml").get_text().strip()
    return text  

# def clean_uni(value):
#     return value.replace("\xa0"," ")

class NewsNbsItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    name = scrapy.Field()
    #     input_processor=MapCompose(unidecode)
    # )
    link = scrapy.Field()
    labels = scrapy.Field()
    content = scrapy.Field()
        # input_processor=MapCompose(remove_tags, remove_n),
        # TakeFirst return the first value not the whole list
        #output_processor=TakeFirst()   
        # )
