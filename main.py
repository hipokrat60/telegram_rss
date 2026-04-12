import os
import requests
import asyncio
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession

# Değişkenler (Railway'den çekilir)
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Kanal listesini temizle (Boşlukları al ve listeye çevir)
KANALLAR_RAW = os.environ.get("KANALLAR", "")
KANALLAR = [k.strip() for k in KANALLAR_RAW.split(',') if k.strip()]

async def main():
    # 1. BAĞLANTI ÇAKIŞMASINI ÖNLEME
    # Railway'de yeni sürüm açılırken eskisinin kapanması için süre tanıyoruz.
    print("n8n Forwarder başlatılıyor, çakışma kontrolü için 15 saniye bekleniyor...")
    await asyncio.sleep(15)

    # Cihaz adını sticker botundan farklı yapıyoruz ki Telegram 'farklı cihaz' saysın
    client = TelegramClient(
        StringSession(STRING_SESSION), 
        API_ID, 
        API_HASH,
        device_model="webhook_n8n_device", # Sticker botundan farklı isim!
        system_version="Linux_Railway_v2"
    )

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
                print(f"Yeni mesaj geldi, medya indiriliyor (ID: {event.id})...")
                media_bytes = await client.download_media(event.media, file=bytes)
                
                if media_bytes:
                    # n8n'de 'Binary Property' ismi 'data' olacak
                    files = {
                        'data': ('image.jpg', media_bytes, 'image/jpeg')
                    }
                    print(f"Medya n8n için hazırlandı ({len(media_bytes)} byte).")
            except Exception as e:
                print(f"Medya indirme hatası: {e}")

        try:
            # n8n'e gönderim (Requests senkron olduğu için loop.run_in_executor ile sarmalamak daha iyidir ama basitlik için direkt bırakıldı)
            # Timeout süresini medya gönderimi için 60 saniye tutuyoruz.
            r = requests.post(WEBHOOK_URL, data=payload, files=files if files else None, timeout=60)
            print(f"n8n Gönderildi. Durum Kodu: {r.status_code}")
        except Exception as e:
            print(f"n8n Webhook hatası: {e}")

    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("KRİTİK HATA: Oturum geçersiz! Lütfen yeni STRING_SESSION alın.")
            return

        print(f"Bot aktif! Dinlenen kanallar: {KANALLAR}")
        print("Görseller n8n'e 'data' ismiyle iletilecek...")
        
        await client.run_until_disconnected()

    except errors.rpcerrorlist.AuthKeyDuplicatedError:
        print("HATA: Oturum başka bir yerden açıldı veya çakışma yaşandı (AuthKeyDuplicated).")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot durduruldu.")
