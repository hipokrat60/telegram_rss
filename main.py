import os
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Değişkenleri Railway Panelinden çekeceğiz
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
# Kanalları virgülle ayırarak yazacağız, burada listeye çeviriyoruz
KANALLAR = os.environ.get("KANALLAR").split(',')

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    # n8n'e gidecek veri paketi
    payload = {
        "kanal": event.chat.title if event.chat else "Bilinmeyen",
        "mesaj": event.raw_text,
        "tarih": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }
    
    try:
        # Veriyi n8n webhook'una gönder
        r = requests.post(WEBHOOK_URL, json=payload)
        print(f"n8n iletildi: {r.status_code}")
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    print("Sistem saniyelik takip modunda çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
