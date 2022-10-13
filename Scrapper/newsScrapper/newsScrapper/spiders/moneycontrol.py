import scrapy
from bs4 import BeautifulSoup
from newsScrapper.items import NewsItem
from newsScrapper.utils.utils import get_stock_id

CONT_DIV = (
    '//*[@id="mc_mainWrapper"]/div[2]/div[2]/div[3]/div[2]/div[2]/div/div[3]/div[1]/div'
)


def get_urls():
    """Get urls for scraping."""
    stocks = ["icici bank", "yes bank"]
    stock_ids = [get_stock_id(stock) for stock in stocks]
    print(stock_ids)
    urls = [
        f"https://www.moneycontrol.com/stocks/company_info/stock_news.php?sc_id={stock_id}&durationType=M&duration=1"
        for stock_id in stock_ids
    ]
    return urls


def text_from_html(data):
    soup = BeautifulSoup(data, "lxml")
    for ticker in soup.find_all("a", class_=["neg", "pos"]):
        ticker.decompose()
    for script in soup.find_all("script"):
        script.decompose()
    texts = soup.findAll(text=True)
    return " ".join(t.strip('\n\t"') for t in texts)


class MoneyControlNews(scrapy.Spider):
    name = "moneycontrolnews"
    allowed_domains = ["www.moneycontrol.com"]
    start_urls = get_urls()

    def parse(self, response):
        news = Selector(text=response.body).xpath(CONT_DIV).get()
        if news == None:
            print("Bruh")
            return
        # for story in stories:
        #     title = Selector(text=story).xpath(STORY_TITLE).get()
        #     link = (
        #         "https://economictimes.indiatimes.com"
        #         + Selector(text=story).xpath(STORY_LINK).get()
        #     )
        #     type = Selector(text=story).xpath(STORY_TYPE).get().split("| ")[1]
        #     date = Selector(text=story).xpath(STORY_DATE).get()
        #     summary = Selector(text=story).xpath(STORY_SUMMARY).get()
        #     yield scrapy.Request(
        #         link,
        #         callback=self.extract_article,
        #         meta={
        #             "title": title,
        #             "link": link,
        #             "type": type,
        #             "date": date,
        #             "summary": summary,
        #         },
        #     )

    def extract_article(self, response):
        html = scrapy.Selector(text=response.body).xpath(ARTICLEDIV).get()
        if html is None:
            return
        data = text_from_html(html)
        news = NewsItem()
        news["title"] = response.meta.get("title")
        news["url"] = response.meta.get("link")
        news["type"] = response.meta.get("type")
        news["date"] = response.meta.get("date")
        news["summary"] = response.meta.get("summary")
        news["article"] = data
        yield news
