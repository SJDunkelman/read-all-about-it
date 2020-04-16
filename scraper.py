'''
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Scraper class which extracts text data from newspaper URLs.
scrape method takes generative URL functions as argument.

Saving uses parquet binary file type -> requires fastparquet or pyarrow library.
'''
from datetime import datetime

import newspaper as nw
import pandas as pd
import re

class Scraper():
    def __init__(self):
        self.request_count = 0
        self.queue = []
        self.results = pd.DataFrame(columns=['title','source','text'])
        self.date = datetime.now()
        
    def add(self, obj):
        self.queue.append(obj)
        
    def scrape(self):
        for source in [self.queue[i].get_urls() for i in range(len(self.queue))]:
            if source:
                for date in source:
                    for url in date:
                        entry = {}
                        article = nw.Article(url)
                        article.download()
                        article.parse()
                        src = re.search('www.(.*).co',url).group(0).replace('.','')
                        entry.update(title=article.title, source=src, text=article.text)
                        self.results = self.results.append(entry,ignore_index=True)
        self.save()
        
    def save(self):
        try:
            self.results.to_parquet('output.parquet.gzip',compression='gzip')
        except:
            self.results.to_csv('output.csv',index=False)
            raise ModuleNotFoundError
        
    def preprocess(self,text):
        # text.lower()
        # tokenise text
        # regex to remove tokens with non-alphabetical
        return text.lower()