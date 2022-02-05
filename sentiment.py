"""
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Creates document-term matrix at headline level.
"""

from nltk.tokenize import word_tokenize
import pandas as pd
import re


class Sentiment:
    def __init__(self):
        # Load Harvard IV/Lasswell Psychosocial dictionary
        self.dictionary = pd.read_csv('inquirerbasic.csv', dtype=str)
        self.dictionary = self.dictionary.iloc[:, :-2]

        # Select Harvard IV dictionary
        self.dictionary = self.dictionary[self.dictionary['Source'].str.contains("H4")]

        # Replace strings with integers
        self.dictionary.iloc[:, 2:] = self.dictionary.iloc[:, 2:].replace(to_replace='[A-Za-z]+', value=1, regex=True)
        self.dictionary = self.dictionary.fillna(0)

        # Load scraper output
        try:
            self.data = pd.read_parquet('output.parquet.gzip')
        except:
            self.data = pd.read_csv('output.csv')

        if self.data.text[0] == "":
            self.full_data = False
        else:
            self.full_data = True

        columns = list(self.dictionary.columns[2:]) + ['Date', 'Source']
        self.sentiment = pd.DataFrame(columns=columns)

        # Preprocess/tokenise data
        for row in self.data.itertuples():
            if self.full_data:
                pass
            data = self.preprocess(row.title)
            result = self.analyse(data)
            if result is not None:
                result = result.append(pd.Series(data=[row.date, row.source], index=['Date', 'Source']))
                self.sentiment = self.sentiment.append(result, ignore_index=True)

    def analyse(self, word_list):
        rows = self.dictionary.loc[self.dictionary.Entry.isin(word_list)]
        if rows.empty:
            print("No relevant words found.")
            return None
        else:
            summed = rows.sum(axis=0)
            return summed[2:]

    def preprocess(self, text):
        text = text.upper()
        text = re.sub(r'[^A-Z]', ' ', text)
        tokens = word_tokenize(text)
        return tokens
