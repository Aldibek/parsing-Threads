
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import urllib.parse
import re
from Keywords  import depression_keywords, emotional_keywords

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
]
options.add_argument(f"user-agent={random.choice(user_agents)}")

url = 'https://www.threads.com/search?q='
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


need = []
df = pd.DataFrame(columns=["Text"])
seen = set()
def search(url):
    try:
        driver.get(url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        time.sleep(random.uniform(1, 3))
        print(f"Parsing posts")
        posts = driver.find_elements(By.XPATH, "//span[@dir='auto' and not(ancestor::div[contains(@style,'--maxHeight')])]")
        for i, post in enumerate(posts):
            try:
                text_of_post = post.text.strip().lower()
                for ui_word in ["like", "reply", "share", "follow", "repost"]:
                    text_of_post = text_of_post.replace(ui_word, "")
                text_of_post = ' '.join(text_of_post.split())
                if not text_of_post:
                    continue
                for need_word in emotional_keywords:
                    if need_word in text_of_post and 10 < len(text_of_post) < 500:
                        if text_of_post not in seen:
                            df.loc[len(df)] = [text_of_post]
                            seen.add(text_of_post)
            except Exception as e_inner:
                continue
        time.sleep(1)
    except Exception as ex:
        print("WRONG", ex)

for index in range(10):
    keyword = random.choice(depression_keywords)
    encoded = urllib.parse.quote(keyword)
    print(f'Searching for posts with the word "{keyword.upper()}"')
    full_url = f"https://www.threads.com/search?q={encoded}"
    search(full_url)
    print(f'Finished parsing posts with the word "{keyword.upper()}", moving on to the next one')

driver.close()
driver.quit()
df.to_csv("threads_posts.csv", index=False, encoding="utf-8")
