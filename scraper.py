"""
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Scraper class which extracts text data from newspaper URLs.
scrape method takes generative URL functions as argument.

Saving uses parquet binary file type -> requires fastparquet or pyarrow library.
"""
from datetime import datetime

import newspaper as nw
import pandas as pd
import re


class Scraper:
    def __init__(self, full_text=False):
        self.request_count = 0
        self.queue = []
        self.results = pd.DataFrame(columns=['title', 'source', 'text', 'date'])
        self.date = datetime.now()
        self.full_text = full_text

    def add(self, obj):
        self.queue.append(obj)

    def scrape(self):
        for source in [self.queue[i].get_urls() for i in range(len(self.queue))]:
            if source:
                for date in source:
                    for url in date:
                        if url:
                            entry = {}
                            article = nw.Article(url)
                            article.download()
                            article.parse()
                            src = re.search(r'(?<=\.)(.*)(?=\.)', url).group(0)
                            if self.full_text:
                                entry.update(title=article.title, source=src, text=article.text,
                                             date=article.publish_date)
                            else:
                                entry.update(title=article.title, source=src, text="", date=article.publish_date)
                            self.results = self.results.append(entry, ignore_index=True)
        self.save()

    def save(self):
        try:
            self.results.to_parquet('output.parquet.gzip', compression='gzip')
        except:
            self.results.to_csv('output.csv', index=False)
            raise ModuleNotFoundError('Saved to csv. To save as a parquet binary file fastparquet or pyarrow must be '
                                      'installed.')
