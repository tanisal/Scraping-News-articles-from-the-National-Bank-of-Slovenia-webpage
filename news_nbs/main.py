from fastapi import FastAPI
from news_nbs.pipelines import NewsNbsPipeline

# Initialising the Fastapi app
app = FastAPI()

#dtabase connection
db_conn = NewsNbsPipeline()

news_data = db_conn.cur.execute("""SELECT * FROM news_db""")
news_data_enumerated=dict((k,v) for k,v in enumerate(news_data,start=1))

@app.get("/items")
def show_news(): 
    return news_data_enumerated

    #making connection with the pipelene database
    #news_data = db_conn.cursor.execute("""SELECT * FROM news_db""")



    # #looping to populate json from the db
    # for i in range(len(news_data)):

    #     d=dict((k,v) for k,v in enumerate(proba,start=1))
    #     jData={}
    #     jData['id']=i+1
    # #     #taking the name attribute
    #     jData['id']['name']= news_data[i][1]
    # #     #looping through all the news
    #     news_data[i]=jData
    # # return news_data



@app.get("/item/{item_id}")
def show_item(item_id:int):
    return news_data_enumerated[item_id]


@app.delete("/item/{item_id}")
def show_item(item_id:int):
    del news_data_enumerated[item_id]