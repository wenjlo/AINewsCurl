import time
from bs4 import BeautifulSoup
from selenium import webdriver
import re,emoji
from config import TOKEN,GROUP_ID,LOG_DIR
from fake_useragent import UserAgent
import requests
import pandas as pd
import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

SCROLL_PAUSE_TIME = 1.8

def user_agent():
    ua = UserAgent(os='windows', browsers='chrome')
    userAgent = ua.chrome
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument(f'user-agent={userAgent}')
    return options

def news_detail(link_url):

    resp = requests.get(link_url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')
    news_title = soup.find('h1', attrs={'class':'title'}).text
    news_content = soup.find("div", attrs={'class':'story'}).find_all("p")
    image_link = soup.find("div", attrs={'class':'story'}).find_all("img")[0]
    image_link = image_link['src']
    if "https:" not in image_link:
        image_link = "https:" + image_link
    text = "\n"
    for p in news_content:
        """
            .string屬性說明：
            (1) 若當前tag節點底下沒有其他tag子節點，會直接抓取內容(返回"NavigableString")
            (2) 若當前tag節點底下只有唯一的一個tag子節點，也會直接抓取tag子節點的內容(返回"NavigableString")
            (3) 但若當前tag節點底下還有很多個tag子節點，.string就無法判斷，(返回"None")
        """
        if ((p.string) is not None):
            text += p.string
            text += '\n'
    return news_title,image_link,text



def news_parser(browser):
    history = pd.read_csv(f"{LOG_DIR}/log.csv")
    html = browser.page_source
    soup = BeautifulSoup(html,"lxml")
    all_news = soup.find("div", attrs={'class': 'block block_1 infinite_scroll'})
    news_block = all_news.find_all('div', attrs={'class': 'piece clearfix'})
    for n in news_block:
        news_body = n.find('h3')
        external_link = news_body.a["href"]
        if external_link not in history['news_url']:
            history = pd.concat([pd.DataFrame([[datetime.datetime.now(),externalLink]],columns=history.columns),history],ignore_index=True)
    history.to_csv(f'{LOG_DIR}/log.csv',index=False)


def insert_news_to_log(title,news_link,image_link,content,llm_content,how_long_ago):
    news_df = pd.read_csv(f'{LOG_DIR}/log.csv')
    news_df = pd.concat([pd.DataFrame([[datetime.datetime.now(), title,news_link,image_link,
                                        content,llm_content,how_long_ago]], columns=news_df.columns), news_df],
                            ignore_index=True)
    news_df.to_csv(f'{LOG_DIR}/log.csv', index=False)

def get_history_news():
    return pd.read_csv(f'{LOG_DIR}/log.csv')


class ETToday:
    def __init__(self):
        self.news_block = None
        self.date_block = None
        self.history_news = None
        self.url = "https://www.ettoday.net/news/focus/生活/"
        self.browser = browser = webdriver.Chrome(service=service, options=options)
        self.last_height = self.browser.execute_script("return document.body.scrollHeight;")
        self.browser.get(self.url)
        self.robot_emoji = emoji.emojize(":robot_face")


    def news_cache(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, "lxml")
        all_news = soup.find("div", attrs={'class': 'block block_1 infinite_scroll'})
        news_block = all_news.find_all('div', attrs={'class': 'piece clearfix'})
        news_df = pd.DataFrame(columns=['time','news_url'])
        for n in news_block:
            news_body = n.find('h3')
            news_link = news_body.a["href"]
            news_df = pd.concat([pd.DataFrame([[datetime.datetime.now(), news_link]], columns=news_df.columns), news_df],
                            ignore_index=True)
        news_df.to_csv(f'{LOG_DIR}/log.csv', index=False)

    def get_recent_news_with_scrolling(self, scroll_count=3):
        """
        使用 Selenium 爬取 ETtoday 網頁，並模擬下滑動作以載入更多新聞。

        Args:
            url (str): 要爬取的網頁 URL。
            scroll_count (int): 模擬下滑的次數。

        Returns:
            list: 包含新聞標題、網址和時間的字典列表。
        """

        # 模擬下滑動作，載入更多新聞
        for i in range(scroll_count):
            print(f"正在執行第 {i + 1} 次下滑...")
            # 模擬按下鍵盤的 END 鍵，直接滑到底部
            self.browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            # 每次下滑後，等待 2 秒讓內容載入
            time.sleep(2)

        news_items = self.browser.find_elements(By.CSS_SELECTOR, 'div.piece.clearfix, div.part_list_3 h3')

        recent_news_links = []

        for item in news_items:
            try:
                # 找到新聞標題和時間
                link_tag = item.find_element(By.TAG_NAME, 'a')
                date_tag = item.find_element(By.CLASS_NAME, 'date')

                if link_tag and date_tag:
                    time_str = date_tag.text.strip()

                    # 判斷時間是否在近一小時內
                    if '分鐘前' in time_str:
                        minutes_ago = int(time_str.split('分鐘前')[0])
                        if minutes_ago <= 60:
                            title = link_tag.text.strip()
                            href = link_tag.get_attribute('href')
                            recent_news_links.append({'title': title, 'url': href, 'time_ago': time_str})

                    if '小時前' in time_str:
                        hours_ago = int(time_str.split('小時前')[0])
                        if hours_ago <= 1:
                            title = link_tag.text.strip()
                            href = link_tag.get_attribute('href')
                            recent_news_links.append({'title': title, 'url': href, 'time_ago': time_str})

            except Exception as e:
                # 忽略那些找不到標籤的項目
                print(e)


        return recent_news_links

    def html(self):
        html = self.browser.page_source
        soup = BeautifulSoup(html, "lxml")
        all_news = soup.find("div", attrs={'class': 'block block_1 infinite_scroll'})

        self.news_block = all_news.find_all('div', attrs={'class': 'piece clearfix'})
        self.date_block = all_news.find_all('span', attrs={'class': 'date'})

    def output(self,chain):
        history = get_history_news()
        news_list = self.get_recent_news_with_scrolling(scroll_count=3)
        for news in news_list:
            if news['url'] not in history['news_url'].values:
                try:
                    title, img_url, content = news_detail(news['url'])

                    llm_content = chain(content)
                    insert_news_to_log(title, news['url'], img_url,content,llm_content.text,news['time_ago'])
                    print(news['title'])
                    print(llm_content.text)
                    print("*****************************************************")
                except Exception as e:
                    print(e)

#
