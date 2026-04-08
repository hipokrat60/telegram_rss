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
    # JSON/Metin verileri
    payload = {
        "channel": str(event.chat.title) if event.chat else "Bilinmeyen",
        "message": str(event.raw_text) or "",
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat and event.chat.username else "Link Yok"
    }

    files = {}
    if event.media:
        try:
            print("Medya indiriliyor...")
            # Medyayı doğrudan bytes olarak hafızaya alıyoruz
            media_bytes = await client.download_media(event.media, file=bytes)
            
            if media_bytes:
                # n8n'de 'Binary Property' ismi 'data' olacak
                files = {
                    'data': ('image.jpg', media_bytes, 'image/jpeg')
                }
                print(f"Medya hazırlandı. İsim: data, Boyut: {len(media_bytes)} byte")
        except Exception as e:
            print(f"Medya indirme hatası: {e}")

    try:
        # n8n'e gönderim
        # 'data' parametresi JSON alanlarını, 'files' parametresi görseli gönderir.
        r = requests.post(WEBHOOK_URL, data=payload, files=files if files else None, timeout=60)
        print(f"n8n Gönderildi. Durum Kodu: {r.status_code}")
    except Exception as e:
        print(f"n8n'e gönderim sırasında hata: {e}")

async def main():
    print("Bot başlatıldı. Görseller n8n'e 'data' ismiyle iletilecek...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Railway ve benzeri sunucular için stabil event loop başlatma
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
