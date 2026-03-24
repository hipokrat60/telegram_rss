import os
import requests
import asyncio
import io
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Değişkenler
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
KANALLAR = os.environ.get("KANALLAR").split(',')

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Sunucuyu kandırmak için tarayıcı kimliği ekliyoruz
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    payload = {
        "source": "Telegram-RSS",
        "channel": event.chat.title if event.chat else "Bilinmeyen",
        "message": event.raw_text or "",
        "date": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }

    files = {}
    if event.photo:
        photo_bytes = await event.download_media(file=io.BytesIO())
        photo_bytes.seek(0)
        files = {'data': ('photo.jpg', photo_bytes, 'image/jpeg')}

    try:
        # HEADERS kısmını burada ekliyoruz
        r = requests.post(WEBHOOK_URL, data=payload, files=files, headers=HEADERS)
        print(f"n8n iletildi: {r.status_code}")
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    print("Sistem bot filtresi aşımı ile çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
