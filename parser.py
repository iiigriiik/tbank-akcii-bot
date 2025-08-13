# parser.py
from sites import tbank, sber
from utils import telegram, storage

def main():
    print("🔍 Запуск парсера акций...")

    sources = [
        ("Т-Банк", tbank.parse_tbank),
        ("СберБанк", sber.parse_sber)
    ]

    seen = storage.load_seen()
    new_promos = []

    for bank_name, parser_func in sources:
        print(f"📌 Парсим {bank_name}...")
        promos = parser_func()
        for promo in promos:
            promo_key = f"{bank_name}_{promo['id']}"
            if promo_key not in seen:
                telegram.send_telegram_message(promo["title"], promo["url"], bank_name)
                seen[promo_key] = True
                new_promos.append(promo)

    storage.save_seen(seen)
    print(f"✅ Готово. Новых акций: {len(new_promos)}")

if __name__ == "__main__":
    main()