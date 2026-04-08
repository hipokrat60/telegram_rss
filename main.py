import os
import requests
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
KANALLAR = os.environ.get("KANALLAR").split(',')

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    # Mesaj metni ve temel bilgiler
    payload = {
        "channel": event.chat.title if event.chat else "Bilinmeyen",
        "message": event.raw_text or "",
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }

    files = None
    if event.media:
        try:
            print("Medya indiriliyor...")
            # bytes olarak indir
            image_data = await client.download_media(event.media, file=bytes)
            
            if image_data:
                # n8n'in en kolay tanıdığı anahtar kelime 'file' dır.
                files = {
                    'file': ('image.jpg', image_data, 'image/jpeg')
                }
                print(f"Medya hazır. Boyut: {len(image_data)} byte")
        except Exception as e:
            print(f"İndirme hatası: {e}")

    try:
        # data=payload (JSON/Form verisi), files=files (Görsel verisi)
        response = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=60)
        print(f"n8n Gönderildi. Durum: {response.status_code}")
    except Exception as e:
        print(f"Gönderim hatası: {e}")

async def main():
    await client.start()
    print("Bot çalışıyor...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
