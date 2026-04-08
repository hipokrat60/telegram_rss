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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    # Spoiler Kontrolü
    # Spoiler bilgisi genellikle event.media üzerinde 'spoiler' özniteliği olarak bulunur.
    is_spoiler = False
    if event.media:
        is_spoiler = getattr(event.media, 'spoiler', False)

    payload = {
        "source": "Telegram-RSS",
        "channel": event.chat.title if event.chat else "Bilinmeyen",
        "message": event.raw_text or "",
        "date": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok",
        "has_spoiler": str(is_spoiler)
    }

    files = {}
    
    # event.photo veya event.document (GIF/Video gibi) kontrolü
    if event.media:
        # Eğer bir medya varsa ve bu bir mesaj (video, foto, gif) ise indir
        print(f"Medya algılandı (Spoiler: {is_spoiler}). İşleniyor...")
        try:
            # BytesIO içine indiriyoruz
            photo_bytes = await event.download_media(file=io.BytesIO())
            
            if photo_bytes:
                photo_bytes.seek(0)
                # Dosya adını ve tipini belirliyoruz. 
                # Genellikle fotoğraflar için 'image/jpeg' uygundur.
                files = {'data': ('media_file.jpg', photo_bytes, 'image/jpeg')}
                print("Medya başarıyla indirildi ve n8n'e hazırlanıyor.")
        except Exception as media_err:
            print(f"Medya indirme hatası: {media_err}")

    try:
        # Not: requests kütüphanesi senkrondur. 
        # Yoğun trafikte 'httpx' veya 'aiohttp' kullanmanız önerilir ancak mevcut yapıyı bozmamak için devam ediyoruz.
        r = requests.post(WEBHOOK_URL, data=payload, files=files, headers=HEADERS, timeout=30)
        print(f"n8n iletildi: Durum Kodu {r.status_code}")
    except Exception as e:
        print(f"n8n'e iletim sırasında hata oluştu: {e}")

async def main():
    print("Sistem spoiler desteği ile çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
