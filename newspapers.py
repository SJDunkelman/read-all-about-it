'''
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Newspaper class for generating urls to pass to scraper class
'''
from datetime import timedelta
import requests
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
    def __init__(self, date, t, base):
        '''
        base = base URL excluding 'HTTPS://www.'
        '''
        self.base = "https://www."+base
        self.date = date
        self.t = t
        
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