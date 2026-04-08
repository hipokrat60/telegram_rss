import os
import requests
import asyncio
import io
import mimetypes
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
    # Spoiler kontrolü
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
    if event.media:
        try:
            print(f"Medya algılandı. Spoiler: {is_spoiler}. İndiriliyor...")
            
            # download_media'da file=bytes kullanmak içeriği doğrudan hafızaya (RAM) alır.
            # Bu, spoilerlı içeriklerde BytesIO'dan daha kararlıdır.
            media_data = await client.download_media(event.media, file=bytes)
            
            if media_data:
                # Dosya uzantısını ve tipini tahmin etmeye çalışalım
                # Varsayılan jpeg, ama video/gif de olabilir
                file_ext = ".jpg"
                mime_type = "image/jpeg"
                
                # Eğer döküman formatındaysa gerçek uzantıyı alalım
                if hasattr(event.media, 'document'):
                    mime_type = event.media.document.mime_type
                    file_ext = mimetypes.guess_extension(mime_type) or ".jpg"

                files = {
                    'data': (f'file{file_ext}', media_data, mime_type)
                }
                print(f"Medya başarıyla indirildi. Boyut: {len(media_data)} bytes")
            else:
                print("Medya verisi boş döndü.")

        except Exception as media_err:
            print(f"Medya indirme hatası: {media_err}")

    try:
        # n8n'e gönderim
        # NOT: 'data' parametresi (payload) ve 'files' (medya) aynı anda gönderilir
        r = requests.post(WEBHOOK_URL, data=payload, files=files, headers=HEADERS, timeout=60)
        print(f"n8n iletildi: Durum Kodu {r.status_code} - Cevap: {r.text[:100]}")
    except Exception as e:
        print(f"n8n iletim hatası: {e}")

async def main():
    print("Bot başlatılıyor... Spoiler ve medya desteği aktif.")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
