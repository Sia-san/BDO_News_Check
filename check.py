import requests
from bs4 import BeautifulSoup
import json
import os
import re
from urllib.parse import urljoin, urlparse, parse_qs


# 黒い砂漠公式お知らせ一覧
URL = "https://www.jp.playblackdesert.com/ja-jp/News/Notice?Page=1&boardType=2&searchText=&searchType="

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 公式サイトからお知らせ一覧を取得
response = requests.get(
    URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()
print("指定URL:", URL)
print("取得URL:", response.url)

print(
    "リダイレクト履歴:",
    [
        (r.status_code, r.url, r.headers.get("Location"))
        for r in response.history
    ]
)

soup = BeautifulSoup(response.text, "html.parser")


# --------------------------------------------------
# お知らせ記事を取得
# --------------------------------------------------

article = None
board_no = None
link = None
title = None

# 新しい公式サイトの記事リンクを探す
for a in soup.select("a[href]"):

    href = a.get("href", "")

    # お知らせ記事のリンクを判定
    if "groupContentNo=" not in href:
        continue

    # 記事番号をURLから取得
    parsed_url = urlparse(href)
    query = parse_qs(parsed_url.query)

    article_no = query.get("groupContentNo", [None])[0]

    if not article_no:
        continue

    # タイトルを取得
    article_title = a.get_text(" ", strip=True)

    if not article_title:
        continue

    # 記事URLを取得
    article_link = urljoin(response.url, href)

    article = a
    board_no = str(article_no)
    link = article_link
    title = article_title

    break


# 記事が取得できなかった場合
if article is None:

    raise Exception(
        "記事取得失敗\n"
        f"URL: {response.url}\n"
        f"ページタイトル: {soup.title}\n"
        "記事リンクが見つかりませんでした。"
    )


# --------------------------------------------------
# state.json に保存するデータ
# --------------------------------------------------

current = {
    "board_no": board_no,
    "link": link
}


# --------------------------------------------------
# 前回の状態を読み込む
# --------------------------------------------------

STATE_FILE = "state.json"

if os.path.exists(STATE_FILE):

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        old = json.load(f)

else:

    old = {}


# --------------------------------------------------
# 新しいお知らせがあるか確認
# --------------------------------------------------

if old.get("board_no") != board_no:

    webhook_url = os.environ["DISCORD_WEBHOOK"]

    discord_response = requests.post(
        webhook_url,
        json={
            "content":
            f"📢 黒い砂漠公式お知らせ更新\n"
            f"{title}\n"
            f"{link}"
        },
        timeout=30
    )

    discord_response.raise_for_status()

    print("新しいお知らせをDiscordに通知しました。")
    print(f"タイトル: {title}")
    print(f"記事番号: {board_no}")
    print(f"URL: {link}")

else:

    print("新しいお知らせはありません。")


# --------------------------------------------------
# state.json を更新
# --------------------------------------------------

with open(
    STATE_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        current,
        f,
        ensure_ascii=False,
        indent=2
    )

print("state.json を更新しました。")
