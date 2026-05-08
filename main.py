import requests
import os

# إعدادات تليجرام
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "last_places_ids.txt" 

# إحداثيات المدينة المنورة
MADINAH_BBOX = "24.25,39.35,24.65,39.85"

def is_sent(place_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, 'r') as f:
        return str(place_id) in f.read()

def save_to_memory(place_id):
    with open(MEMORY_FILE, 'a') as f:
        f.write(str(place_id) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    icon = "☕️" if ptype == "cafe" else "🍽"
    label = "كافيه جديد" if ptype == "cafe" else "مطعم جديد"
    map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    
    message = (
        f"{icon} <b>رادار طيبة رصد لك: {label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📍 الاسم:</b> {name}\n"
        f"<b>🏙 المدينة:</b> المدينة المنورة\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طيبة للجديد - طلال التقني</i>"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": "🗺 فتح في الخريطة", "url": map_link}]]
        }
    }
    requests.post(url, json=payload)

def hunt_places():
    print("🚀 جاري فحص المدينة المنورة...")
    
    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"~"cafe|restaurant"]({MADINAH_BBOX});
      way["amenity"~"cafe|restaurant"]({MADINAH_BBOX});
    );
    out center;
    """
    
    # قائمة خوادم بديلة في حال تعطل الأساسي
    urls = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    
    headers = {'User-Agent': 'MadinahRadarBot/1.0 (Contact: talal@example.com)'}
    
    success = False
    for url in urls:
        if success: break
        try:
            print(f"محاولة الاتصال بالخادم: {url}")
            response = requests.post(url, data={'data': query}, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                places = data.get('elements', [])
                print(f"📊 وجدنا {len(places)} مكان.")
                
                count = 0
                for p in places:
                    p_id = p.get('id')
                    tags = p.get('tags', {})
                    name = tags.get('name')
                    ptype = tags.get('amenity')
                    lat = p.get('lat') or p.get('center', {}).get('lat')
                    lon = p.get('lon') or p.get('center', {}).get('lon')
                    
                    if name and not is_sent(p_id):
                        send_to_telegram(name, ptype, lat, lon)
                        save_to_memory(p_id)
                        count += 1
                        if count >= 10: break 
                
                print(f"✅ تم إرسال {count} مكان جديد.")
                success = True
            elif response.status_code == 429:
                print("⚠️ الخادم مشغول (Too Many Requests)، جاري تجربة خادم آخر...")
            else:
                print(f"❌ فشل الخادم بكود: {response.status_code}")
        except Exception as e:
            print(f"❌ خطأ عند الاتصال بـ {url}: {e}")

if __name__ == "__main__":
    hunt_places()
