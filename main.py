import requests
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "places_memory.txt"
# تغطية شاملة للمدينة من العزيزية للمطار
MADINAH_BBOX = "24.15,39.25,24.80,40.00"

def is_sent(pid):
    if not os.path.exists(MEMORY_FILE): return False
    with open(MEMORY_FILE, 'r') as f: return str(pid) in f.read()

def save_to_memory(pid):
    with open(MEMORY_FILE, 'a') as f: f.write(str(pid) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    icon = "☕️" if ptype == "cafe" else "🍽"
    map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    share_url = f"https://t.me/share/url?url={map_link}&text=كافيه جديد فتح بالمدينة! 📍"
    
    message = (
        f"{icon} <b>رادار طيبة للجديد:</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📱 الاسم:</b> {name}\n"
        f"<b>🏙 المدينة:</b> المدينة المنورة\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طلال التقني - تغطية شاملة</i>"
    )
    
    payload = {
        "chat_id": CHAT_ID, "text": message, "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "🗺 فتح في الخريطة", "url": map_link}], [{"text": "🚀 مشاركة بالستوري", "url": share_url}]]}
    }
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json=payload)

def hunt_places():
    query = f'[out:json];(node["amenity"~"cafe|restaurant"]({MADINAH_BBOX});way["amenity"~"cafe|restaurant"]({MADINAH_BBOX}););out center;'
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}, timeout=30).json()
        for p in response.get('elements', []):
            tags = p.get('tags', {})
            name = tags.get('name')
            if name and not is_sent(p['id']):
                lat = p.get('lat') or p.get('center', {}).get('lat')
                lon = p.get('lon') or p.get('center', {}).get('lon')
                send_to_telegram(name, tags.get('amenity'), lat, lon)
                save_to_memory(p['id'])
    except: print("فشل الاتصال بالخريطة، سيتم المحاولة لاحقاً.")

if __name__ == "__main__":
    hunt_places()
