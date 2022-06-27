# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3

class NewsNbsPipeline(object):

    def __init__(self):
        self.conn = sqlite3.connect('news.db')
        self.cur = self.conn.cursor()
        self.create_table()


    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS news_db(
        date TEXT,
        name TEXT,
        link TEXT,
        labels TEXT, 
        content TEXT 
        )""")
    
    
    def process_item(self, item, spider):

        self.cur.execute("""
        INSERT INTO news_db (date, name, link, labels, content) VALUES (?, ?, ?, ?, ?);
        """,
        (
            str(item['date']),
            str(item['name']),
            str(item['link']),
            str(item['labels']),
            str(item['content'])
        ))

        self.conn.commit()
        return item

  
   