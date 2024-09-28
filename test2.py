import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager  # Import webdriver-manager
import getpass
import os
import time
import logging
import bs4
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import unicodedata

# [Logging setup remains the same]

# Set username.
user = getpass.getuser()

# List of Facebook URLs to scrape
facebook_urls = [
    "https://www.facebook.com/profeMikhailKrasnov",
    "https://www.facebook.com/groups/164639504222784",
    "https://www.facebook.com/positivafmradio",
    "https://www.facebook.com/groups/6669773836451212"
]

def clean_text(text):
    """
    Remove accents, special characters, and convert to lowercase.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')
    # Remove special characters
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def add_colon_between_names(text):
    return re.sub(r"([a-z])([A-Z])", r"\1: \2", text)

class Selenium:
    def __init__(self, driver):
        self.driver = driver
        self.unique_comments = set()

    def extract_posts(self):
        results = []
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            start_time = time.time()
            end_time = start_time + 60
            while time.time() < end_time:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                posts = soup.find_all("div", class_="x78zum5 x1n2onr6 xh8yej3")

                for post in posts:
                    post_content = post.find("div", class_="x1iorvi4 x1pi30zi x1l90r2v x1swvt13")
                    comments = post.find_all("div", class_="x1y1aw1k xn6708d xwib8y2 x1ye3gou")
                    
                    if post_content:
                        clean_post = clean_text(post_content.text)
                        for comment in comments:
                            clean_comment = clean_text(comment.text)
                            if clean_comment not in self.unique_comments:
                                self.unique_comments.add(clean_comment)
                                results.append((clean_post, clean_comment))
        except Exception as e:
            logger.error(f"Error scraping posts: {e}")
        return results

    def open_Facebook_posts(self, url):
        self.driver.get(url)
        time.sleep(5)

    def close_browser(self):
        self.driver.quit()

def scrape_facebook():
    os.system("taskkill /im chrome.exe /f")  # Kill existing Chrome instances if any
    user = getpass.getuser()
    
    # Use webdriver-manager to automatically manage the ChromeDriver
    options = Options()
    options.add_argument(f"--user-data-dir=C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--profile-directory=Default")
    
    # Set up the WebDriver with ChromeDriverManager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    selenium = Selenium(driver=driver)

    all_results = []

    for url in facebook_urls:
        selenium.open_Facebook_posts(url)
        results = selenium.extract_posts()
        all_results.extend([(url, post, comment) for post, comment in results])
        print(f"Data extracted for {url}")

    selenium.close_browser()
    print("All data has been extracted")

    return all_results

def train_sentiment_model():
    # Load the original dataset and train the model
    df = pd.read_excel('data/BBDD.xlsx')
    df = df[['sentimiento', 'review_es']].copy()

    # Clean the text in the original dataset
    df['review_es'] = df['review_es'].apply(clean_text)

    target_map = {'positivo': 1, 'negativo': 0}
    df['target'] = df['sentimiento'].map(target_map)

    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(max_features=2000)
    X_train = vectorizer.fit_transform(df_train['review_es'])
    Y_train = df_train['target']

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, Y_train)

    return vectorizer, model

def sentiment_analysis(scraped_data, vectorizer, model):
    # Convert scraped data to DataFrame
    df = pd.DataFrame(scraped_data, columns=['URL', 'Post', 'Comment'])

    # Transform the scraped comments using the same vectorizer
    X_scraped = vectorizer.transform(df['Comment'])

    # Predict sentiment for scraped comments
    df['Sentiment'] = model.predict(X_scraped)

    # Map numeric predictions back to text labels
    sentiment_map = {0: 'negativo', 1: 'positivo'}
    df['Sentiment'] = df['Sentiment'].map(sentiment_map)

    # Save the result to a new CSV file
    df.to_csv('facebook_posts_sentiment_analysis.csv', index=False)

    print("Sentiment analysis completed. Results saved to 'facebook_posts_sentiment_analysis.csv'")

if __name__ == "__main__":
    scraped_data = scrape_facebook()
    vectorizer, model = train_sentiment_model()
    sentiment_analysis(scraped_data, vectorizer, model)
