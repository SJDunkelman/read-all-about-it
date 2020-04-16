'''
For Distribution and Modification see GNU General Public License v3.0.
Credit: Simon Dunkelman (www.github.com/SJDunkelman)

Add newspaper sources to queue for scraping
'''

from scraper import Scraper
from newspapers import Guardian

## Hyperparameters
TIME_FRAME = 7

if __name__ == "__main__":
    
    bot = Scraper()
    
    ## Add instances of newspapers to scraper
    bot.add(Guardian(bot.date,TIME_FRAME))
    
    # Scrape all newspapers in queue
    bot.scrape()