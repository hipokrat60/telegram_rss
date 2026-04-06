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
    # Spoiler Kontrolü (Opsiyonel Loglama)
    is_spoiler = False
    if event.media and hasattr(event.media, 'spoiler'):
        is_spoiler = event.media.spoiler

    payload = {
        "source": "Telegram-RSS",
        "channel": event.chat.title if event.chat else "Bilinmeyen",
        "message": event.raw_text or "",
        "date": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok",
        "has_spoiler": str(is_spoiler)
    }

    files = {}
    if event.photo:
        print(f"Yeni görsel algılandı (Spoiler: {is_spoiler}). İndiriliyor...")
        try:
            # Spoiler her ne kadar istemci tarafında olsa da, 
            # asıl (temiz) görüntüyü çekmek için explicitly en büyük olanı hedefliyoruz.
            # download_media fonksiyonu, thumb parametresi verilmezse en yüksek çözünürlüklü orijinali çeker.
            photo_bytes = await event.download_media(file=io.BytesIO())
            
            if photo_bytes:
                photo_bytes.seek(0)
                # n8n binary veri olarak 'data' isminde alacağı için bu şekilde bırakıyoruz
                files = {'data': ('photo.jpg', photo_bytes, 'image/jpeg')}
                print("Görsel başarıyla indirildi.")
        except Exception as media_err:
            print(f"Medya indirme hatası: {media_err}")

    try:
        # n8n webhook'una verileri ve dosyayı iletiyoruz
        r = requests.post(WEBHOOK_URL, data=payload, files=files, headers=HEADERS, timeout=30)
        print(f"n8n iletildi: Durum Kodu {r.status_code}")
    except Exception as e:
        print(f"n8n'e iletim sırasında hata oluştu: {e}")

async def main():
    print("Sistem bot filtresi aşımı ve spoiler çözümü ile çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    # asyncio.run(main()) bazen event loop hataları verebilir, Railway için daha stabil bir yapı:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
