import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.jp.playblackdesert.com/ja-JP/News/Notice?boardType=2"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=30).text

soup = BeautifulSoup(html, "html.parser")

article = soup.select_one("ul.thumb_nail_list li a")

if article is None:
    raise Exception("記事取得失敗")

board_no = article.get("data-boardno")
link = article.get("href")

title = article.select_one("strong.title span.line_clamp").get_text(strip=True)

current = {
    "board_no": board_no,
    "link": link
}

STATE_FILE = "state.json"

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
            f"📢 黒い砂漠公式お知らせ更新\n{link}"
        }
    )

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False)
