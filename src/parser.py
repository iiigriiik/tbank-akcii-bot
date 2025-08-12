# src/parser.py
# Автоматический парсер акций Т-Банка

import requests
from bs4 import BeautifulSoup
import html
import re
import os
from datetime import datetime
import time

# === НАСТРОЙКИ ===
# Токен и ID канала будут браться из config.py
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

BLOG_URL = "https://www.tbank.ru/finance/blog/"
DATA_FILE = "../data/sent_promos.txt"  # На уровень выше, в папке data

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# === ФУНКЦИИ ===
def load_sent_urls():
    if not os.path.exists(DATA_FILE):
        return set()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"⚠️ Ошибка чтения: {e}")
        return set()

def save_sent_url(url):
    try:
        with open(DATA_FILE, "a", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception as e:
        print(f"⚠️ Ошибка записи: {e}")

def get_article_excerpt(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return "Текст недоступен"

        soup = BeautifulSoup(response.text, "html.parser")
        content = soup.find("div", class_="Article__content")
        if not content:
            content = soup.find("div", {"data-pb-type": "content"})

        if content:
            paragraphs = content.find_all("p", limit=3)
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            text = re.sub(r'\s+', ' ', text).strip()
            return (text[:280] + "...") if len(text) > 280 else text
        else:
            return "Подробности по ссылке"
    except Exception as e:
        return "Ошибка при загрузке текста"

def send_to_telegram(title, url, description=""):
    safe_title = html.escape(title)
    safe_desc = html.escape(description)

    message = f"""
🚀 <b>Новая акция от Т‑Банка!</b>

📌 <b>{safe_title}</b>

{safe_desc}

🔗 <a href="{url}">Подробнее на сайте</a>
    """.strip()

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(api_url, data=data, timeout=10)
        if response.status_code == 200:
            return True, None
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

# === ЗАПУСК ===
print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск parser.py...")

sent_urls = load_sent_urls()
new_count = 0

try:
    response = requests.get(BLOG_URL, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.find_all("a", href=True)
    new_promos = []

    for link in links:
        href = link["href"]
        if href.startswith("/finance/blog/") and len(href) > 20:
            full_url = "https://www.tbank.ru" + href
            if full_url not in sent_urls:
                title_elem = link.find("h3") or link.find(class_=re.compile("Typography", re.I))
                title = title_elem.get_text(strip=True) if title_elem else "Новая акция"
                if len(title) > 100:
                    title = title[:100] + "..."
                new_promos.append((title, full_url))

    new_promos = list(set(new_promos))
    print(f"🔍 Найдено новых: {len(new_promos)}")

    for title, url in new_promos:
        print(f"📄 Загружаю: {title}")
        desc = get_article_excerpt(url)
        success, error = send_to_telegram(title, url, desc)
        if success:
            print(f"✅ Отправлено: {title}")
            save_sent_url(url)
            new_count += 1
            time.sleep(1.5)
        else:
            print(f"❌ Ошибка: {title} → {error}")

except Exception as e:
    print(f"💥 Ошибка: {e}")

print(f"✅ Готово. Новых акций: {new_count}")