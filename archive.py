import json
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

DOMAIN = "https://programmerscareer.com/"
# Medium RSS feed URL
RSS_URL = "https://wesley-wei.medium.com/feed"
# 存储文章的文件路径
STORED_ARTICLES_FILE = "../blog/draft/articles.json"
# 轮询间隔时间（秒）
# POLL_INTERVAL = 24 * 60 * 60  # 一天

def load_stored_articles():
    """加载已存储的文章信息"""
    try:
        with open(STORED_ARTICLES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_articles(articles):
    """将文章信息保存到本地文件"""
    with open(STORED_ARTICLES_FILE, "w", encoding="utf-8") as file:
        json.dump(articles, file, ensure_ascii=False, indent=4)

def fetch_rss_feed(url):
    """从 RSS URL 获取文章信息"""
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        articles.append({
            "title": entry.title.replace("’", "'"),
            "link": entry.link.split('?')[0],
            "published": entry.published if "published" in entry else str(datetime.now())
        })
    return articles

def find_new_articles(stored_articles, fetched_articles, web_articles):
    """对比已存储的文章和新获取的文章，返回新增的文章"""
    stored_titles = {article["title"] for article in stored_articles}
    for article in fetched_articles:
        for web_article in web_articles:
            if article["title"] == web_article["title"]:
                article["web_link"] = web_article["link"]
    new_articles = [article for article in fetched_articles if article["title"] not in stored_titles]
    return new_articles

def fetch_titles_and_links(url):
    """
    从指定的 URL 中提取文章标题和链接。
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}, status code: {response.status_code}")
            return []

        # 解析 HTML 内容
        soup = BeautifulSoup(response.content, "html.parser")
        # 提取文章
        articles = []
        for article in soup.find_all("h6", class_="title is-6"):
            link_tag = article.find("a")  # 查找 <a> 标签
            if link_tag:
                title = link_tag.text.strip()  # 获取标题
                link = link_tag["href"]       # 获取链接
                link = DOMAIN + link    # 构造完整链接
                articles.append({"title": title, "link": link})

        # print(f"Fetched {articles} articles from {url}")
        return articles

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def main():
    print(f"Fetching RSS feed at {datetime.now()}...")
    # 加载已存储的文章
    stored_articles = load_stored_articles()
    # 获取新的文章
    fetched_articles = fetch_rss_feed(RSS_URL)

    # 调用函数抓取网站的标题和链接
    web_articles = fetch_titles_and_links("https://programmerscareer.com/archives/")
    web_articles += fetch_titles_and_links("https://programmerscareer.com/archives/page/2/")

    # 找到新增的文章
    new_articles = find_new_articles(stored_articles, fetched_articles, web_articles)
    if new_articles:
        print(f"Found {len(new_articles)} new articles!")
        # 将新文章追加到已存储的文章中
        stored_articles.extend(new_articles)
        save_articles(stored_articles)
        # 打印新文章信息
        for article in new_articles:
            print(f"New Article: {article['title']} - {article['link']}")
    else:
        print("No new articles found.")


if __name__ == "__main__":
    main()
