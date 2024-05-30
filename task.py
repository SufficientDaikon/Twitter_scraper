import time
import re
import sched
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import argparse

def setup_driver():  # setting up the selenium driver
    service = Service(ChromeDriverManager("125.0.6422.113").install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_ticker_mentions(driver, url, ticker):
    driver.get(url)  # navigating to the twitter account page
    time.sleep(2)  # wait for page to load
    last_height = driver.execute_script("return document.body.scrollHeight") # get page scroll height 
    ticker_pattern = re.compile(
        r'\$\b' + re.escape(ticker) + r'\b', re.IGNORECASE)
    mention_count = 0

    #find tweets and search them
    while True:
        try:
            tweets = driver.find_elements(
                By.XPATH, '//div[@data-testid="tweetText"]')
            for tweet in tweets:
                if ticker_pattern.search(tweet.text):
                    mention_count += 1
        except Exception as e:
            print(e)

        #scroll to the botoom of the page
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # wait for page to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        # break loop if at page bottom
        if new_height == last_height:
            break
        last_height = new_height

    return mention_count


def main(scheduler, twitter_accounts, ticker, interval):
    driver = setup_driver()
    total_mentions = 0
    #iterate over each account
    for account in twitter_accounts:
        print("Now scraping", account)
        url = f"https://twitter.com/{account}"
        mentions = scrape_ticker_mentions(driver, url, ticker)
        total_mentions += mentions

    print(
        f"'{ticker}' was mentioned '{total_mentions}' times in the last '{interval}' minutes.")
    #schudle the script to run again in 15 minutes
    scheduler.enter(interval * 60, 1, main, (scheduler,
                    twitter_accounts, ticker, interval))

# add a command line arg for ticker
parser = argparse.ArgumentParser(
    description="Scrape Twitter for ticker mentions.")
parser.add_argument("--ticker")
args = parser.parse_args()
if args.ticker is None:
    parser.error("--ticker is required")

twitter_accounts = [
    'Mr_Derivatives', 'warrior_0719', 'ChartingProdigy', 'allstarcharts',
    'yuriymatso', 'TriggerTrades', 'AdamMancini4', 'CordovaTrades',
    'Barchart', 'RoyLMattox'
]
ticker = args.ticker
interval = 15


s = sched.scheduler(time.time, time.sleep)
main(s, twitter_accounts, ticker, interval)
s.run()
