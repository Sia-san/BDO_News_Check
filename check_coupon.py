import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.jp.playblackdesert.com/ja-JP/News/Notice?boardType=1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=30).text

soup = BeautifulSoup(html, "html.parser")

articles = soup.select("ul.thumb_nail_list li a")

coupon_article = None

for article in articles:

    title = article.get_text(" ", strip=True)

    if "クーポン" in title:
        coupon_article = article
        break

if coupon_article is None:
    raise Exception("クーポン記事が見つからない")

board_no = coupon_article.get("data-boardno")
link = coupon_article.get("href")
title = coupon_article.get_text(" ", strip=True)

current = {
    "board_no": board_no
}

STATE_FILE = "state_coupon.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        old = json.load(f)
else:
    old = {}

if old.get("board_no") != board_no:

    requests.post(
        os.environ["DISCORD_WEBHOOK"],
        json={
            "content":
            f"🎟️ 新しいクーポン記事を検知\n"
            f"【{title}】\n\n"
            f"{link}"
        }
    )

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False)
