import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


def setup_driver():  # setting up the selenium driver
    service = Service(ChromeDriverManager("125.0.6422.113").install())
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=service, options=options)
    return driver





def scrape_ticker_mentions(driver, url, ticker):
    driver.get(url) #navigating to the twitter page
    time.sleep(2)  # Allow time for page to load
    last_height = driver.execute_script("return document.body.scrollHeight")
    ticker_pattern = re.compile(
        r'\$\b' + re.escape(ticker) + r'\b', re.IGNORECASE)
    mention_count = 0

    while True:
        try:
            tweets = driver.find_elements(
                By.XPATH, '//div[@data-testid="tweetText"]')
            for tweet in tweets:
                if ticker_pattern.search(tweet.text):
                    mention_count += 1
        except Exception as e:
            print(e)

        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow time for new tweets to load

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return mention_count

def main(twitter_accounts, ticker, interval):
    driver = setup_driver()
    while True:
        total_mentions = 0
        for account in twitter_accounts:
            url = f"https://twitter.com/{account}"
            mentions = scrape_ticker_mentions(driver, url, ticker)
            total_mentions += mentions

        print(
            f"'{ticker}' was mentioned '{total_mentions}' times in the last '{interval}' minutes.")
        time.sleep(interval * 60)
    driver.quit()


if __name__ == "__main__":
    twitter_accounts = [
        'Mr_Derivatives', 'warrior_0719', 'ChartingProdigy', 'allstarcharts',
        'yuriymatso', 'TriggerTrades', 'AdamMancini4', 'CordovaTrades',
        'Barchart', 'RoyLMattox'
    ]
    ticker = 'TSLA'
    interval = 15  

    main(twitter_accounts, ticker, interval)
