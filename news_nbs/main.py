from fastapi import FastAPI 
from news_nbs.pipelines import NewsNbsPipeline # Scrapy pipeline Instance

# Initialising the Fastapi app
app = FastAPI()

#database connection with the scrapy pipeline object
db_conn = NewsNbsPipeline()

#incoming data from sqlite database from the pipeline of the scrapy project
news_data = db_conn.cur.execute("""SELECT * FROM news_db ORDER BY date""")
#creating id's for the entries of the database and formating them for easy to use afterwards
news_data_enumerated=dict((k,v) for k,v in enumerate(news_data,start=1))

#Decorator for the get request of all items
@app.get("/items")
def show_news(): 
    return news_data_enumerated

#Decorator for the get Request of the specific item
@app.get("/item/{item_id}")
def show_item(item_id:int):
    return news_data_enumerated[item_id]



#Decorator for the delete request of the api
@app.delete("/item/{item_id}")
def show_item(item_id:int):
    #deleting the json entry with the item_id 
    del news_data_enumerated[item_id]