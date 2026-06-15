import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os

URL = "https://www.jp.playblackdesert.com/ja-JP/News/Detail?groupContentNo=7077"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(URL, headers=headers, timeout=30).text

soup = BeautifulSoup(html, "html.parser")

content = soup.select_one(".fr-view")

if content is None:
    raise Exception("記事本文取得失敗")

text = content.get_text("\n", strip=True)

current_hash = hashlib.sha256(
    text.encode("utf-8")
).hexdigest()

current = {
    "hash": current_hash
}

STATE_FILE = "state_coupon.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        old = json.load(f)
else:
    old = {}

if old.get("hash") != current_hash:

    requests.post(
        os.environ["DISCORD_WEBHOOK"],
        json={
            "content":
            "🎟️ クーポンページ更新検知\n\n"
            f"{URL}"
        }
    )

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False)
