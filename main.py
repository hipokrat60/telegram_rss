import os
import requests
import asyncio
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
    # Metin verilerini hazırlıyoruz
    payload = {
        "channel": str(event.chat.title) if event.chat else "Bilinmeyen",
        "message": str(event.raw_text) or "",
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }

    files = None
    if event.media:
        try:
            print("Medya indiriliyor...")
            # Medyayı bytes olarak indir
            image_data = await client.download_media(event.media, file=bytes)
            
            if image_data:
                # n8n'de 'Binary Property' kısmına yazacağınız isim: 'file'
                files = {
                    'file': ('image.jpg', image_data, 'image/jpeg')
                }
                print(f"Medya hazır. Boyut: {len(image_data)} byte")
        except Exception as e:
            print(f"Medya indirme hatası: {e}")

    try:
        # n8n'e POST gönderimi
        # 'data' metinleri, 'files' görseli temsil eder
        r = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=60)
        print(f"n8n Gönderildi. Durum: {r.status_code}")
    except Exception as e:
        print(f"Webhook gönderim hatası: {e}")

async def main():
    print("Bot aktif... Görsel göndermeye hazır.")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
