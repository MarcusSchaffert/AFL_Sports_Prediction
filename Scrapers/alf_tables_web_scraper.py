from Scrapers.web_scraper import WebScraper


class AFLTablesWebScraper(WebScraper):

    def __init__(self, url):
        super().__init__(url)

    def hello(self):
        print('hello')
