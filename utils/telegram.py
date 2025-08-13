# utils/telegram.py
import requests
from config import BOT_TOKEN, CHANNEL_ID

def send_telegram_message(title, url, bank):
    text = f"""
🚀 <b>Новая акция от {bank}!</b>

📌 <b>{title}</b>

🔗 <a href="{url}">Перейти к акции</a>
    """
    url_tg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    response = requests.post(url_tg, data=data)
    if response.status_code == 200:
        print(f"✅ Отправлено: {title[:50]}...")
    else:
        print(f"❌ Ошибка Telegram: {response.status_code}, {response.text}")