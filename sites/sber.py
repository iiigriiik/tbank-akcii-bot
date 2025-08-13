# sites/sber.py
import requests
from bs4 import BeautifulSoup
import html
import re

def parse_sber():
    url = "https://www.sberbank.ru/ru/person/promo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # На Сбере акции часто в div с классом, содержащим "promo"
        promo_blocks = soup.find_all("div", class_=re.compile("promo", re.I))

        results = []
        seen_ids = set()

        for block in promo_blocks[:5]:
            link_tag = block.find("a", href=True)
            if not link_tag:
                continue

            href = link_tag["href"]
            full_url = href if href.startswith("https") else "https://www.sberbank.ru" + href

            title_tag = block.find("h3") or block.find("h2") or block.find("div", string=True)
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            title = html.unescape(title)
            title = re.sub(r'\s+', ' ', title)

            # Уникальный ID — последняя часть URL
            promo_id = href.strip("/").split("/")[-1]
            if not promo_id or promo_id in seen_ids:
                continue
            seen_ids.add(promo_id)

            results.append({
                "id": promo_id,
                "title": title,
                "url": full_url,
                "bank": "СберБанк"
            })

        return results

    except Exception as e:
        print(f"[Сбер] Ошибка: {e}")
        return []