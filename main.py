from telethon import TelegramClient, events
import requests
import asyncio

# --- AYARLAR ---
API_ID = 31424536           # 1. Adımdaki ID
API_HASH = 'a2c09d60c2cb4e698fa4aadc77b464dc' # 1. Adımdaki Hash
N8N_WEBHOOK_URL = 'https://n8n.batuhanboran.com/webhook-test/promosyon-servis' # 2. Adımdaki URL

# Takip edilecek kanal listesi (Kullanıcı adları @ olmadan)
KANALLAR = ['hellcase', 'kanal_2'] 
# ---------------

client = TelegramClient('n8n_session', API_ID, API_HASH)

@client.on(events.NewMessage(chats=KANALLAR))
async def handler(event):
    # Mesaj içeriğini n8n'e gönderilecek formata getir
    payload = {
        "kanal": event.chat.title if event.chat else "Bilinmeyen Kanal",
        "mesaj": event.raw_text,
        "tarih": str(event.date),
        "link": f"https://t.me/{event.chat.username}/{event.id}" if event.chat.username else "Link Yok"
    }

    try:
        # Veriyi n8n Webhook'una POST et
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        print(f"n8n'e gönderildi: {response.status_code}")
    except Exception as e:
        print(f"n8n hatası: {e}")

async def main():
    print("Dinleme başladı...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
