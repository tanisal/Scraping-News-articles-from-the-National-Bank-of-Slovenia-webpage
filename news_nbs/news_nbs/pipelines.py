# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
import sqlite3

class NewsNbsPipeline(object):
    #Initialising the database
    def __init__(self):
        #initialsing connection , making the thread to false, cause we will need
        # more connections for the FastAPI requests 
        self.conn = sqlite3.connect('news.db',check_same_thread=False)
        #initialising the cursor
        self.cur = self.conn.cursor()
        #initialising the table
        self.create_table()

    #Defining the database table
    def create_table(self):
        #Table with all the columns needed
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS news_db(
        date TEXT,
        name TEXT PRIMARY KEY,
        link TEXT,
        labels TEXT, 
        content TEXT 
        )""")
    
    # Sending all the colleted data frm the item into the database and commiting it
    def process_item(self, item, spider):

        self.cur.execute("""
        INSERT OR IGNORE INTO news_db (date, name, link, labels, content) VALUES (?, ?, ?, ?, ?);
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

  
   