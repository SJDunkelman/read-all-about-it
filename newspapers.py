"""
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Newspaper class for generating urls to pass to scraper class
"""
import requests
import re
from datetime import datetime
import random
import time

from datetime import timedelta
from selenium import webdriver
from bs4 import BeautifulSoup

headers = {'User-Agent':
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}


# Helper functions
def two_digit_string(n):
    if n < 10:
        return '0' + str(n)
    else:
        return str(n)


def month_to_str(m):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    return months[m - 1]


# Base class: Newspaper
class Newspaper:
    def __init__(self, date, t, base, button_xpath=None, topics=[]):
        """
        base = base URL excluding 'HTTPS://www.'
        t = number of days prior to date to scrape
        button_xpath = If selenium used to itneract with load more, store full
        """
        self.base = "https://www." + base
        self.date = date
        self.t = t
        self.button_xpath = button_xpath
        self.topics = topics
        if self.topics == []:
            self.selective = False
        else:
            self.selective = True

    def get_urls(self):
        """
        Method should be overwritten dependent on how articles are archived by url pattern
        d, m, y are all integers for day, month and year of first date included
        t is integer for number of previous days to scrape

        Should use lxml HTML parser for speed.
        """
        raise NotImplementedError

    def minus_day(self, delta):
        """
        Returns day, month, year which should be assigned in get_urls
        """
        new_date = self.date - timedelta(days=delta)
        return (new_date.day, new_date.month, new_date.year)


# Test class
class Test(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="test.com/uk-news/")

    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + '/' + month_to_str(month) + '/' + two_digit_string(day) + '/all'
            urls.append([archive_url])
        return urls


# Define custom classes for each news source below
class Guardian(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="theguardian.com/uk-news/")

    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + '/' + month_to_str(month) + '/' + two_digit_string(day) + '/all'

            # Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text

            # Parse soup for page
            soup = BeautifulSoup(archive_page, "lxml")

            # Extract all links within div class="fc-container__inner"
            content_links = soup.find_all("a", {"class": "fc-item__link"})
            urls.append([content_links[i]['href'] for i in range(len(content_links))])
        return urls


class NYPost(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="nypost.com/news/",
                         button_xpath="/html/body/div[1]/div[4]/div[2]/div/div[1]/div/div[1]/div[2]/div/div/div/a")

    def get_urls(self):
        urls = []
        final_date = self.date - timedelta(days=self.t)
        page = 1
        in_range = True
        while in_range:
            archive_url = self.base + "page/" + str(page) + "/"
            # Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text
            # Parse soup for page
            soup = BeautifulSoup(archive_page, "lxml")

            for entry in soup.find_all("div", {"class": "entry-header"}):
                # Check if post date out of range
                current_date = entry.find('p').text
                end_index = current_date.find(' |')
                current_date = current_date[:end_index]
                current_date = datetime.strptime(current_date, "%B %d, %Y")
                if current_date < final_date:
                    in_range = False
                    break
                # Get URL from thumbnail
                url = entry.find('a')['href']
                urls.append(url)

            page += 1
        return urls


class WSJ(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="wsj.com/news/archive/",
                         topics=['u.s.', 'tri-state area', 'u.s. economy'])

    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            archive_url = self.base + str(year) + two_digit_string(month) + two_digit_string(day)
            # Get request for archive url
            archive_page = requests.get(archive_url, headers=headers).text
            # Parse soup for page
            soup = BeautifulSoup(archive_page, "lxml")

            for entry in soup.find_all("article", {"class": "WSJTheme--story--XB4V2mLz"}):
                if self.selective:
                    # Check if post is in desired topic
                    current_topic = entry.find("div", {"class": "WSJTheme--articleType--34Gt-vdG"}).text.lower()
                    if self.topics.count(current_topic):
                        url = entry.find('a')['href']
                        urls.append(url)
                else:
                    url = entry.find('a')['href']
                    urls.append(url)
        return urls


class LATimes(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="latimes.com/sitemap/",
                         topics=['story'])

    def get_urls(self):
        urls = []
        months = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            months.append(month)
        months = set(months)

        final_date = self.date - timedelta(self.t)

        for idx, month in enumerate(months):
            # Extract first page of month
            archive_url = self.base + str(year) + "/" + two_digit_string(month)
            archive_page = requests.get(archive_url, headers=headers).text
            soup = BeautifulSoup(archive_page, "lxml")

            # Get number of pages for month
            page_menu_div = soup.find("div", {"class": "ArchivePage-pagination"})

            pages = [link.text for link in page_menu_div.find_all('a')]

            page_iter = iter(pages)

            while True:
                try:
                    # Iterate element of pages
                    page = next(page_iter)

                    # Scrape new page of month
                    archive_url = self.base + str(year) + "/" + two_digit_string(month) + "?p=" + page
                    archive_page = requests.get(archive_url, headers=headers).text
                    soup = BeautifulSoup(archive_page, "lxml")

                    content_box = soup.find("ul", {"class": "ArchivePage-menu"})
                    for article in content_box.find_all("a"):
                        url = article['href']
                        if idx == len(months) - 1:
                            # Check if dates are in range
                            article_date_str = re.search(r'(\d\d\d\d+-\d\d+-\d\d)', url)
                            if article_date_str:
                                article_date = datetime.strptime(article_date_str.group(0), "%Y-%m-%d")
                                if article_date >= final_date:
                                    # Check if topic is relevant
                                    article_topic_str = re.search(r'com\/(.*?)\/\d', url).group(1)
                                    article_topics = article_topic_str.split('/')
                                    if any(topic in article_topics for topic in self.topics):
                                        urls.append(url)
                                else:
                                    raise StopIteration
                        else:
                            urls.append(url)
                except StopIteration:
                    break

        return urls


class DailyMail(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="dailymail.co.uk/home/sitemaparchive/day_",
                         topics=['story'])

    def get_urls(self):
        urls = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)

            archive_url = self.base + str(year) + two_digit_string(month) + two_digit_string(day) + ".html"
            archive_page = requests.get(archive_url, headers=headers).text
            soup = BeautifulSoup(archive_page, "lxml")

            content_box = soup.find("ul", {"class": "archive-articles debate link-box"})
            for article in content_box.find_all("a"):
                url = article['href']

                # Extract topics from article URL
                article_topic_str = re.search(r'(?<=\/)(.*)(?=\/article)', url)
                if article_topic_str is not None:
                    article_topics = article_topic_str.group(0).split('/')
                    if any(topic in article_topics for topic in self.topics):
                        urls.append(url)
                else:
                    article_topics = None

                print(article_topics)

        return urls


class NYTimes(Newspaper):
    def __init__(self, date, t):
        super().__init__(date, t,
                         base="nytimes.com/search?dropmab=true&endDate=",
                         button_xpath="/html/body/div[1]/div[2]/main/div[1]/div[2]/div[2]/div/button")

    def get_urls(self):
        urls = []

        start_day, start_month, start_year = self.minus_day(self.t)
        end_day, end_month, end_year = self.minus_day(0)

        # Load page for date range to scrape
        section = "&query=&sections=U.S.%7Cnyt%3A%2F%2Fsection%2Fa34d3d6c-c77f-5931-b951-241b4e28681c&sort=oldest&startDate="
        archive_url = self.base + str(end_year) + two_digit_string(end_month) + two_digit_string(
            end_day) + section + str(start_year) + two_digit_string(start_month) + two_digit_string(start_day)
        print(archive_url)

        # Load all content on archive page by clicking 'load more' button
        driver = webdriver.Chrome('./chromedriver')
        driver.get(archive_url)

        while True:
            try:
                load_more_button = driver.find_element_by_xpath(self.button_xpath)
                time.sleep(random.randint(1, 5))
                load_more_button.click()
                time.sleep(random.randint(1, 5))
            except Exception as e:
                print(e)
                break

        # Scrape links from archive page
        archive_html = driver.page_source
        soup = BeautifulSoup(archive_html, "lxml")

        content_box = soup.find("ol", {"data-testid": "search-results"})
        for article in content_box.find_all("li", {"class": "css-1l4w6pd"}):
            url = "https://www.nytimes.com/" + article.find("a")['href']
            urls.append(url)

        return urls


class MotherJones(Newspaper):
    """
    Assumes date range is within the same year
    """

    def __init__(self, date, t):
        super().__init__(date, t,
                         base="motherjones.com/",
                         topics=['politics'])

    def get_urls(self):
        urls = []
        # Get months in date range
        months = []
        for subtract_days in range(self.t):
            day, month, year = self.minus_day(subtract_days)
            months.append(month)
        months = set(months)

        for topic in self.topics:
            for month in months:
                archive_url = self.base + topic + "/" + str(year) + "/" + two_digit_string(month)
                archive_page = requests.get(archive_url, headers=headers).text
                soup = BeautifulSoup(archive_page, "lxml")

            for entry in soup.find_all("h3", {"class": "hed"}):
                url = entry.find('a')['href']
                urls.append(url)
        return urls

# class PBS(Newspaper):
#    def __init__(self, date, t):
#        super().__init__(date, t, 
#                         base = "https://www.pbs.org/newshour/",
#                         topics = ['nation'])
#    
#    def get_urls(self):
#        urls = []        
#
#        final_date = self.date - timedelta(self.t)        
#        page = 1
#        
#        for topic in self.topics:   
#            while True:
#                try:
#                    archive_url = self.base + topic + "/page/" + str(page)
#                    archive_page = requests.get(archive_url, headers=headers).text
#                    soup = BeautifulSoup(archive_page,"lxml")
#                    
#                    # Get number of pages for month
#                    content_box = soup.find("div",{"class":"archive__cards "})
#                        for article in content_box.find_all("article"):
#                            # Check date is in range
#                            article_date_str = article.find("p").text
#                            article_date_str = re.search(r'(\w{3} \d\d)',article_date_str).group(0)
#                            article_date = 
#                            
#                            url = article['href']
#                            if idx == len(months)-1:
#                                # Check if dates are in range
#                                article_date_str = re.search(r'(\d\d\d\d+-\d\d+-\d\d)',url)
#                                if article_date_str:
#                                    article_date = datetime.strptime(article_date_str.group(0),"%Y-%m-%d")
#                                    if article_date >= final_date:
#                                        # Check if topic is relevant
#                                        article_topic_str = re.search(r'com\/(.*?)\/\d',url).group(1)
#                                        article_topics = article_topic_str.split('/')
#                                        if any(topic in article_topics for topic in self.topics):
#                                            urls.append(url)
#                                    else:
#                                        raise StopIteration
#                            else:
#                                urls.append(url)
#                    except StopIteration:
#                        break
#
#        return urls 
#        
#
# 'class="border-top-off border-top-100-pct border-bottom-hairline border-bottom-100-pct "'
