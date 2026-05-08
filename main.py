import requests
import os

# إعدادات تليجرام
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "places_memory.txt"

# إحداثيات المدينة المنورة (نطاق واسع يغطي أغلب الأحياء)
# [جنوب، غرب، شمال، شرق]
MADINAH_BBOX = "24.30,39.40,24.60,39.80"

def is_sent(place_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, 'r') as f:
        return str(place_id) in f.read()

def save_to_memory(place_id):
    with open(MEMORY_FILE, 'a') as f:
        f.write(str(place_id) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    # تحديد الأيقونة حسب النوع
    icon = "☕️" if ptype == "cafe" else "🍽"
    label = "كافيه جديد" if ptype == "cafe" else "مطعم جديد"
    
    # رابط جوجل ماب بالإحداثيات
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
    print("جاري فحص المدينة المنورة عن أماكن جديدة...")
    
    # استعلام Overpass لجلب الكافيهات والمطاعم في المدينة
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="cafe"]({MADINAH_BBOX});
      node["amenity"="restaurant"]({MADINAH_BBOX});
    );
    out body;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}).json()
        places = response.get('elements', [])
        
        for p in places:
            p_id = p.get('id')
            tags = p.get('tags', {})
            name = tags.get('name', 'مكان غير مسمى')
            ptype = tags.get('amenity')
            lat = p.get('lat')
            lon = p.get('lon')
            
            # إذا كان المكان له اسم ولم يتم إرساله من قبل
            if name != 'مكان غير مسمى' and not is_sent(p_id):
                send_to_telegram(name, ptype, lat, lon)
                save_to_memory(p_id)
                print(f"✅ تم رصد: {name}")
                
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات: {e}")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("خطأ: تأكد من إضافة السيكريتس")
    else:
        hunt_places()
