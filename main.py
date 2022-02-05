"""
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Add newspaper sources to queue for scraping
"""

from scraper import Scraper
from newspapers import Guardian, NYPost, WSJ, LATimes, NYTimes, MotherJones
from timeit import default_timer as timer
from datetime import date

# Hyperparameters
FIRST_DATE = date(2020, 1, 1) # datetime.now().date()
LAST_DATE = date(2020, 4, 24)
TIME_FRAME = (LAST_DATE - FIRST_DATE).days

# System Timer
start = timer()

if __name__ == "__main__":
    bot = Scraper(full_text=False)

    # Add instances of UK news sources to scraper
    bot.add(Guardian(bot.date, TIME_FRAME))
    bot.add(WSJ(bot.date, TIME_FRAME))
    bot.add(LATimes(bot.date, TIME_FRAME))
    bot.add(NYTimes(bot.date, TIME_FRAME))
    bot.add(MotherJones(bot.date, TIME_FRAME))

    # Scrape all newspapers in queue
    bot.scrape()
    end = timer()
    print("Scraping took", end - start, "seconds")
