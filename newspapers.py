'''
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Newspaper class for generating urls to pass to scraper class
'''
import requests
from datetime import datetime
import random

from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

headers = {'User-Agent': 
           'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}

## Helper functions
def two_digit_string(n):
    if n < 10:
        return '0'+str(n)
    else:
        return str(n)

def month_to_str(m):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    return months[m-1]

## Base class: Newspaper
class Newspaper():
    def __init__(self, date, t, base, button_xpath=None, topics=[]):
        '''
        base = base URL excluding 'HTTPS://www.'
        t = number of days prior to date to scrape
        button_xpath = If selenium used to itneract with load more, store full 
        '''
        self.base = "https://www."+base
        self.date = date
        self.t = t
        self.button_xpath = button_xpath
        self.topics = topics
        if self.topics == []:
            self.selective = False
        else:
            self.selective = True
        
    def get_urls(self):
        '''
        Method should be overwritten dependent on how articles are archived by url pattern
        d, m, y are all integers for day, month and year of first date included
        t is integer for number of previous days to scrape
        
        Should use lxml HTML parser for speed.
        '''
        raise NotImplementedError
    
    def minus_day(self, delta):
        '''
        Returns day, month, year which should be assigned in get_urls
        '''
        new_date = self.date - timedelta(days=delta)
        return (new_date.day,new_date.month,new_date.year)

## Test class
class Test(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t, 
                         base = "test.com/uk-news/")
    
    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + '/' + month_to_str(month) + '/' + two_digit_string(day) + '/all'
            urls.append([archive_url])
        return urls

## Define custom classes for each news source below
class Guardian(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t, 
                         base = "theguardian.com/uk-news/")
    
    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + '/' + month_to_str(month) + '/' + two_digit_string(day) + '/all'
            
            ## Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text
            
            ## Parse soup for page
            soup = BeautifulSoup(archive_page,"lxml")
            
            ## Extract all links within div class="fc-container__inner"
            content_links = soup.find_all("a", {"class":"fc-item__link"})
            urls.append([content_links[i]['href'] for i in range(len(content_links))])
        return urls
    
class NYPost(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t, 
                         base = "nypost.com/news/",
                         button_xpath="/html/body/div[1]/div[4]/div[2]/div/div[1]/div/div[1]/div[2]/div/div/div/a")
    
    def get_urls(self):
        urls = []
        final_date = self.date - timedelta(days=self.t)
        page = 1
        in_range = True
        while in_range:
            archive_url = self.base + "page/" + str(page) + "/"            
            ## Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text
            ## Parse soup for page
            soup = BeautifulSoup(archive_page,"lxml")
            
            for entry in soup.find_all("div", {"class":"entry-header"}):
                ## Check if post date out of range
                current_date = entry.find('p').text
                end_index = current_date.find(' |')
                current_date = current_date[:end_index]
                current_date = datetime.strptime(current_date, "%B %d, %Y")
                if current_date < final_date:
                    in_range = False
                    break
                ## Get URL from thumbnail
                url = entry.find('a')['href']
                urls.append(url)
                
            page += 1
        return urls
    
class WSJ(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t, 
                         base = "wsj.com/news/archive/",
                         topics = ['u.s.','tri-state area','u.s. economy'])
    
    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + two_digit_string(month) + two_digit_string(day)
            ## Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text
            ## Parse soup for page
            soup = BeautifulSoup(archive_page,"lxml")
            
            for entry in soup.find_all("article", {"class":"WSJTheme--story--XB4V2mLz"}):
                if self.selective:
                    ## Check if post is in desired topic
                    current_topic = entry.find("div", {"class":"WSJTheme--articleType--34Gt-vdG"}).text.lower()
                    if self.topics.count(current_topic):
                        url = entry.find('a')['href']
                        urls.append(url)
                else:
                    url = entry.find('a')['href']
                    urls.append(url)
        return urls