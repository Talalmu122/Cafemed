import requests
import os

# الإعدادات من السيكريتس
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "places_memory.txt"

# نطاق المدينة المنورة كاملاً (من العزيزية للمطار)
MADINAH_BBOX = "24.15,39.25,24.80,40.00"

def is_sent(pid):
    if not os.path.exists(MEMORY_FILE): return False
    with open(MEMORY_FILE, 'r') as f: return str(pid) in f.read()

def save_to_memory(pid):
    with open(MEMORY_FILE, 'a') as f: f.write(str(pid) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    icon = "☕️" if ptype == "cafe" else "🍽"
    label = "كافيه جديد" if ptype == "cafe" else "مطعم جديد"
    
    # روابط جوجل ماب والمشاركة الذكية
    map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    share_url = f"https://t.me/share/url?url={map_link}&text=شوف الكافيه الجديد اللي صاده رادار طلال في المدينة! 📍"
    
    message = (
        f"{icon} <b>رادار طيبة رصد لك: {label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📱 الاسم:</b> {name}\n"
        f"<b>🏙 المدينة:</b> المدينة المنورة\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طلال التقني - تغطية شاملة</i>"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🗺 فتح في الخريطة", "url": map_link}],
                [{"text": "🚀 مشاركة بالستوري", "url": share_url}]
            ]
        }
    }
    requests.post(url, json=payload)

def hunt_places():
    print("🚀 جاري فحص المدينة المنورة...")
    # استعلام متطور يجلب (النقاط والمباني) لضمان الدقة
    query = f'[out:json][timeout:30];(node["amenity"~"cafe|restaurant"]({MADINAH_BBOX});way["amenity"~"cafe|restaurant"]({MADINAH_BBOX}););out center;'
    
    # خوادم الخرائط
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    try:
        response = requests.post(overpass_url, data={'data': query}).json()
        elements = response.get('elements', [])
        
        count = 0
        for p in elements:
            name = p.get('tags', {}).get('name')
            p_id = p.get('id')
            
            if name and not is_sent(p_id):
                lat = p.get('lat') or p.get('center', {}).get('lat')
                lon = p.get('lon') or p.get('center', {}).get('lon')
                
                send_to_telegram(name, p.get('tags', {}).get('amenity'), lat, lon)
                save_to_memory(p_id)
                count += 1
                if count >= 10: break # يرسل 10 أماكن كحد أقصى في كل فحص
        
        print(f"✅ تم إرسال {count} أماكن جديدة.")
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")

if __name__ == "__main__":
    hunt_places()
