from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd


# A generic web scraper class that primarily scrapes information from websites that have tables.
# Such tables have headers and row data which are some of the main variables used in this class.
#
class WebScraper:
    TABLE_ELEMENT = 'table'
    TABLE_HEADER_ELEMENT = 'th'
    TABLE_ROW_ELEMENT = 'tr'
    TABLE_HEAD_ELEMENT = 'thead'
    TABLE_BODY_ELEMENT = 'tbody'
    TABLE_DATA_ELEMENT = 'td'
    DIV_ELEMENT = 'div'
    SPAN_ELEMENT = 'span'

    ELEMENT_ID = 'id'
    ELEMENT_CLASS = 'class'

    #DRIVER_TEST = 'C:/Program Files (x86)/Google/Chrome/Application/chromedriver'
    DRIVER = webdriver.Chrome('C:/Program Files (x86)/Google/Chrome/Application/chromedriver')
    headers = None
    rows_data = None
    url = None
    soup = None
    content = None
    table = None
    table_row_counter = None
    df = None

    def __init__(self, url):
        self.headers = []
        self.rows_data = []
        self.url = url
        self.table_row_counter = 0
        self.DRIVER.get(self.url)
        content = self.DRIVER.page_source
        self.soup = BeautifulSoup(content)

    def create_dataframe_from_scraped_table_data(self, row_data, headers):
        """
        :param headers: A list that stores the headers for particular rows
        :type headers: str list
        :param row_data: A list that stores data collected from the rows of a table. The list should contain strings.
        :type headers: str list
        :return: a dataframe which has columns from the headers list and row data from row_data list
        """
        self.handle_columns_with_same_name()
        self.df = pd.DataFrame(columns=headers)
        values_list = []
        count = 0
        for value in row_data:
            if count == len(headers) - 1:
                new_row = {}
                values_list.append(value)
                for i, row_value in enumerate(values_list):
                    try:
                        new_row[headers[i]] = row_value
                    except:
                        print('Fail')
                self.df = self.df.append(new_row, ignore_index=True)
                values_list = []
            elif count == len(headers):
                count = 0
                values_list.append(value)
            else:
                values_list.append(value)
            count += 1

    def handle_columns_with_same_name(self):
        for header_value in self.headers:
            count = 0
            for index, compare_head_value in enumerate(self.headers):
                if header_value == compare_head_value:
                    count += 1
                if count > 1:
                    self.headers[index] += '_' + str(count)

    def save_dataframe(self, filename):
        assert isinstance(self.df, pd.DataFrame)
        self.df.to_csv(filename, index=False)

    def set_url_to_scrape(self, website):
        assert isinstance(website, str)
        self.url = website
        self.DRIVER.get(self.url)
        content = self.DRIVER.page_source
        self.soup = BeautifulSoup(content)

    def reset_variables(self):
        self.headers = []
        self.rows_data = []
        self.table_row_counter = 0

    def end_scraper(self):
        self.DRIVER.quit()

