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

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    # Spoiler bilgisi (varsa)
    is_spoiler = getattr(event.media, 'spoiler', False) if event.media else False

    payload = {
        "source": "Telegram-RSS",
        "channel": event.chat.title if event.chat else "Bilinmeyen",
        "message": event.raw_text or "",
        "date": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok",
        "has_spoiler": str(is_spoiler)
    }

    files = {}
    if event.media:
        try:
            print("Medya algılandı, indiriliyor...")
            # Telethon'un kendi iç mekanizmasıyla en doğru formatta indiriyoruz
            # file=bytes kullanarak doğrudan hafızaya alıyoruz
            media_bytes = await client.download_media(event.media, file=bytes)
            
            if media_bytes:
                # Telegram'ın dosyaya verdiği gerçek uzantıyı bulalım (.jpg, .png, .webp vb.)
                # Eğer uzantı bulunamazsa varsayılan .jpg yapalım
                ext = event.file.ext if event.file else ".jpg"
                mime_type = event.file.mime_type if event.file else "image/jpeg"
                
                filename = f"image{ext}"
                
                files = {
                    'data': (filename, media_bytes, mime_type)
                }
                print(f"Medya başarıyla hazırlandı: {filename} ({len(media_bytes)} bytes)")
            
        except Exception as media_err:
            print(f"Medya işleme hatası: {media_err}")

    try:
        # n8n'e gönderim - Timeout'u 60 saniyeye çıkardık (büyük görseller için)
        r = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=60)
        print(f"n8n Sonuç: {r.status_code}")
    except Exception as e:
        print(f"Gönderim hatası: {e}")

async def main():
    print("Sistem çalışıyor. Görsel formatı otomatik algılanıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
