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
    # Metin verilerini hazırla
    payload = {
        "kanal": event.chat.title if event.chat else "Bilinmeyen",
        "mesaj": event.raw_text or "",
        "tarih": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }

    files = {}
    # Eğer mesajda fotoğraf varsa
    if event.photo:
        print("Görsel indiriliyor...")
        # Görseli RAM belleğe indir (dosya oluşturmadan)
        photo_bytes = await event.download_media(file=io.BytesIO())
        photo_bytes.seek(0) # Okuma kafasını başa sar
        # n8n'e gönderilecek dosya sözlüğü
        files = {'data': ('photo.jpg', photo_bytes, 'image/jpeg')}

    try:
        # Hem metni (data) hem de dosyayı (files) n8n'e gönder
        # Not: Dosya gönderirken 'json=' yerine 'data=' kullanmak daha sağlıklıdır
        r = requests.post(WEBHOOK_URL, data=payload, files=files)
        print(f"n8n iletildi: {r.status_code}")
    except Exception as e:
        print(f"Hata: {e}")

async def main():
    print("Sistem medya desteği ile çalışıyor...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
