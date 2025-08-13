# sites/tbank.py
import requests
from bs4 import BeautifulSoup
import html
import re

def parse_tbank():
    url = "https://www.tbank.ru/finance/blog/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Ищем карточки акций — обычно в <a> с датой и заголовком
        articles = soup.find_all("a", href=lambda x: x and "/finance/blog/" in x)
        results = []

        for art in articles[:5]:  # Берём 5 самых свежих
            title_tag = art.find("h3") or art.find("div", class_="Typography")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            title = html.unescape(title)
            title = re.sub(r'\s+', ' ', title)

            link = "https://www.tbank.ru" + art["href"]

            # ID акции — по ссылке (уникальный)
            promo_id = art["href"].strip("/").split("/")[-1]

            results.append({
                "id": promo_id,
                "title": title,
                "url": link,
                "bank": "Т-Банк"
            })

        return results

    except Exception as e:
        print(f"[Т-Банк] Ошибка: {e}")
        return []