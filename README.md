# Scraping News articles from the National Bank of Slovenia webpage

![Project image](https://user-images.githubusercontent.com/50557141/176175441-6c2dc03c-1792-4305-9e15-bbad6189cb4b.png)

The project is focused on gathering news information from the National Bank of Slovenia webpage and storing it in a database, which is then displayed in a REST API using FastAPI.

---

### Table of Contents

- [Dependencies](#dependencies)
- [Setting the spider](#setting-the-spider)
- [Setting the pipelines](#setting-the-pipelines)
- [FastAPI creation](#fastapi-creation)
- [FastAPI](#fastapi)

---

## Dependencies

Please see the ``requirements.txt`` of the project for the whole list of  dependencies.

Main important components used:

- Python 3.10.40
- Scrapy 2.6.1
- FastApi 0.78.0

[Back To The Top](#scraping-news-articles-from-the-national-bank-of-slovenia-webpage)

---

## Setting the spider

### Checking the webpage

First step in the project is to check the webpage of the news we want to scrape
```
    https://nbs.sk/en/press/news-overview/
```
Inspecting it i saw that the page is dynamic and in that sense i need to dive deeper to gather the content. Checking the Network's Fetch/XHR i saw the following POST request loading:
```
    https://nbs.sk/wp-json/nbs/v1/post/list?_locale=us
```

![Screenshot main](https://user-images.githubusercontent.com/50557141/176175570-7ff07fb5-97ea-48bc-8a08-3336d03f0f4b.png)


### Post Request

On that request  the response data is in a json format and in that json file there is a html part i need. To gather it i will make a post request with all the needed headers, copied from the webpage. 

```
    def start_requests(self):
        urls = "https://nbs.sk/wp-json/nbs/v1/post/list?_locale=user"

        yield scrapy.Request(
            url=urls,
            method="POST",
            headers=self.headers,
            body=self.payload,
            callback=self.parse,
        )
```
### Parse Function - first layer
Then the response i use to parse the json data and later on grab all the need info for the news articles, using the following function

```
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
                # don't filter 
                yield response.follow(a, callback=self.parse_content, meta={"item":item },dont_filter = True)
                
```
Looping through all the links on the page i gathered the needed info of every single article, then store it is the item instance, that i created in ``items.py``.

```
class NewsNbsItem(scrapy.Item):
    # define the fields for your item here like:
    date = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    labels = scrapy.Field()
    content = scrapy.Field()
        
```

The problem here lies in that, i can not crawl over the content of the articles, i need to go on second level of the webpage for each article. 
i make that sending all the link to another parse function, using the meta attribute of the item, so that i could append the second layer content info to the item.

### Parse Function - second layer



```

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
            step3 = step2.replace("\n", "").replace("\t\t\t","")
            #removing the html tags/ bs4 wors better here that w3lib.html
            step4= remove_tags(step3)
            step5= re.sub(' +', ' ', step4)
            #saving the content, clening the unicode giberish
            item["content"] = [unidecode(step5)]
        except:
            #if i don find a website with paragpahs , then receiving exeption
            item["content"] = "Not a valid news content"
        #returning all the collected data from level one and two
        yield item
```

Then i go over the content, clean it and check if there is links with no normal content and raising an exeption. At the end i am returning the crawled item instance.


[Back To The Top](#scraping-news-articles-from-the-national-bank-of-slovenia-webpage)

## Setting the pipelines

### Initialising the database
I use sqlite for the database setting of the scrapy pipeline instance. 
The steps are straight forward :
- Initialise the database connection
- Initialising the cursor
- Adding "create_table" method

```
class NewsNbsPipeline(object):
    def __init__(self):
        self.conn = sqlite3.connect('news.db',check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()

```
### Defining the database table
Setting the appropriate colums for the items gathered

```
    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS news_db(
        date TEXT,
        name TEXT PRIMARY KEY,
        link TEXT,
        labels TEXT, 
        content TEXT 
        )""")
```
### Commiting all the data to the database
Important is to use OR IGNORE not to duplicate the database entries


```
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

```
That is all for the pipeline part

[Back To The Top](#scraping-news-articles-from-the-national-bank-of-slovenia-webpage)

## FastAPI Creation

I created a ``api.py`` file for the API in the project folder.
I created two GET and one DELETE methods . One of the GET methods is for all the news we have. The other is for certain id's news. The DELETE method is  deleting news article witha certain id.

### Creting the API instance
In order to see the results i will need a server. That is why i install uvicorn for that reason.

![Project image](https://raw.githubusercontent.com/tomchristie/uvicorn/master/docs/uvicorn.png)

Making a connection with the scrapy's pipeliine, i creted beforehand

```

app = FastAPI()
db_conn = NewsNbsPipeline()
news_data = db_conn.cur.execute("""SELECT * FROM news_db ORDER BY date""")

```
### Convinient JSON formating
Here one important thing is that if i have an ordered json file with the id's of the news articles with  has as a dictionary all the info for that article , it will be pretty easy to use the methods afterwars. That is why i use the following dictionary comprehansion:

```
news_data_enumerated=dict((k,v) for k,v in enumerate(news_data,start=1))

```

### Fast API Methods

Then i use it in the methods as follows:

GET all the items method
```
@app.get("/items")
def show_news(): 
    return news_data_enumerated

```
GET certain id item

```
@app.get("/item/{item_id}")
def show_item(item_id:int):
    return news_data_enumerated[item_id]
```
DELETE certain item
``` 
@app.delete("/item/{item_id}")
def show_item(item_id:int):
    #deleting the json entry with the item_id 
    del news_data_enumerated[item_id]
```

the uvicorn server needs to be started like this:

``` 
uvicorn api:app --reload
```

[Back To The Top](#scraping-news-articles-from-the-national-bank-of-slovenia-webpage)

## FastAPI

The results of the craling project can be seen on the 127.0.0.1:8000/docs with all the methods created.

It looks like this.

![FastAPI result](https://user-images.githubusercontent.com/50557141/176177028-b430ec75-9dd2-4248-a5e9-9f6236197b52.png)


and a view over the results for getting all lthe news articels.

![FastAPI Result2](https://user-images.githubusercontent.com/50557141/176177202-4e245783-68d7-43b3-81ab-bd60ac277cc7.png)


[Back To The Top](#scraping-news-articles-from-the-national-bank-of-slovenia-webpage)
