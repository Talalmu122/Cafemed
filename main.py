import requests
import os

# إعدادات تليجرام
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
# تأكد أن هذا الاسم هو نفس الموجود في جيت هاب أو اتركه وهو سينشئه تلقائياً
MEMORY_FILE = "last_places_ids.txt" 

# إحداثيات المدينة المنورة (توسيع النطاق قليلاً)
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
    
    # استعلام مطور يبحث عن (النقطة والمبنى) معاً لضمان صيد كل شيء
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"cafe|restaurant"]({MADINAH_BBOX});
      way["amenity"~"cafe|restaurant"]({MADINAH_BBOX});
    );
    out center;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}).json()
        places = response.get('elements', [])
        print(f"📊 عدد الأماكن اللي لقاها الرادار: {len(places)}")
        
        count = 0
        for p in places:
            p_id = p.get('id')
            tags = p.get('tags', {})
            name = tags.get('name')
            ptype = tags.get('amenity')
            
            # جلب الإحداثيات سواء كانت نقطة أو مركز مبنى
            lat = p.get('lat') or p.get('center', {}).get('lat')
            lon = p.get('lon') or p.get('center', {}).get('lon')
            
            if name and not is_sent(p_id):
                send_to_telegram(name, ptype, lat, lon)
                save_to_memory(p_id)
                count += 1
                if count >= 5: break # نرسل 5 أماكن فقط في كل مرة عشان ما ينحظر البوت
                
        print(f"✅ تم إرسال {count} مكان جديد للقناة.")
                
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات: {e}")

if __name__ == "__main__":
    hunt_places()
