

<p align="center">
    <h1>Read All About It</h1>
    <h3 >Newspaper Text Data Scraper</h3>
</p>
---
<p align="center">
 <em>🗞 Library for scraping news data from major newspapers in US & UK. </em>
</p>

Gather <i>complete text data</i> including headlines and full article text over for <i>Natural Language Processing</i> projects.

URLs for individual articles are scraped from the news site, then the library <code> newspaper3k  </code> is used to curate article content.

This project was originally intended to be used to track the relationship between the sentiment of Covid-19 related articles in reported news and returns in the stock market, therefore in <code>sentiment.py </code> the Harvard IV/Lasswell Pyschosocial dictionary is loaded and may be used to create a basic Document-Term matrix. The intention was to further expand this with feature-based sentiment analysis (pre-reading content included in repo for interested parties) but this project has now been abandoned for the foreseeable future.

##### Newspapers Supported

📰🇬🇧	Guardian

📰🇺🇸	NYPost

📰🇺🇸	WallStreetJournal

📰🇺🇸	LATimes

📰🇺🇸	NYTimes

📰🇺🇸	MotherJones

~~📰🇺🇸	PBS~~ [Unfinished]

📰🇬🇧🇺🇸	DailyMail

The original intention was to gather data from a much larger group both geographically and politically, but the underlying research project was abandoned as a matter of priority. If you would like me to add a newspaper source please add it as an issue and I will add it.

 I make no promise of maintenance if existing newspaper sites change.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Development](#development)

## Installation

----

```bash
git clone https://github.com/SJDunkelman/newspaper_scraper.git
cd newspaper_scraper
```

## Usage

----

Due to the sequential nature of news site layouts the articles must be found and downloaded from today back to a date of your choosing.

In <code>main.py</code> change <code>LAST_DATE</code> to the date you would like to scrape backwards to.

Then run in Terminal:

```bash
python main.py
```



#### Output

If the <code>fastparquet</code> or <code>pyarrow</code> library is installed then the dataframe will be saved as a parquet binary file, reducing size. If not, the final dataframe is saved as a CSV file and looks like (if <code>full_text=True</code> for Scraper):

|         Title         | Source   |            Text            | Date     |
| :-------------------: | -------- | :------------------------: | -------- |
| Man arrested after... | Guardian | Three men were arrested... | 1/1/2020 |
| New record set in...  | Guardian | A new world record was...  | 1/1/2020 |

## Development

----

The base class of <code>Newspaper </code> in <code>newspapers.py</code> makes it quick and easy to add a new newspaper source, and at the time of creation (2020) the already completed examples covered all general layouts news sites typically use. On each news site you typically either browse all articles chronologically by altering a URL pattern, or you simulate endless scrolling on a load on scroll dynamic web page.

