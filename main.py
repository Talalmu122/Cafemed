import requests
import os

# إعدادات تليجرام - تأكد من إضافتها في Secrets بجيت هاب
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "places_memory.txt"

# إحداثيات المدينة المنورة الجديدة والأوسع بناءً على الصورة
# تم توسيع النطاق ليشمل العزيزية، أبار علي، طريق المطار، والمدينة كاملة تقريباً.
# [جنوب، غرب، شمال، شرق]
MADINAH_BBOX_WIDE = "24.15,39.25,24.80,40.00"

def is_sent(place_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, 'r') as f:
        return str(place_id) in f.read()

def save_to_memory(place_id):
    with open(MEMORY_FILE, 'a') as f:
        f.write(str(place_id) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    # تحديد الأيقونة والتسمية
    if ptype == "cafe":
        icon = "☕️"
        label = "كافيه جديد رصده الرادار!"
    elif ptype == "restaurant":
        icon = "🍽"
        label = "مطعم جديد رصده الرادار!"
    else:
        icon = "📍"
        label = "مكان جديد"

    # رابط جوجل ماب بالإحداثيات المباشرة
    map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    
    # تنسيق الرسالة بشكل جمالي ومحسن بصرياً
    message = (
        f"{icon} <b>رادار طيبة للجديد: {label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📱 الاسم:</b> {name}\n"
        f"<b>🏙 المدينة:</b> المدينة المنورة\n"
        f"<b>📌 الموقع:</b> {lat:.4f}, {lon:.4f}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طلال التقني - رصد المدينة المنورة كاملة</i>"
    )
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": "🗺 فتح الموقع في الخريطة", "url": map_link}]]
        }
    }
    
    requests.post(url, json=payload)

def hunt_places():
    print(f"🚀 جاري فحص المدينة المنورة (نطاق واسع) عن أماكن جديدة...")
    
    # استعلام Overpass المطور لجلب الكافيهات والمطاعم في النطاق الجديد الأوسع
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="cafe"]({MADINAH_BBOX_WIDE});
      node["amenity"="restaurant"]({MADINAH_BBOX_WIDE});
    );
    out body;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}).json()
        places = response.get('elements', [])
        print(f"📊 وجد الرادار {len(places)} مكان في النطاق الجديد.")
        
        count = 0
        for p in places:
            p_id = p.get('id')
            tags = p.get('tags', {})
            name = tags.get('name', 'مكان غير مسمى')
            ptype = tags.get('amenity')
            lat = p.get('lat')
            lon = p.get('lon')
            
            # إذا كان المكان له اسم ولم يتم إرساله من قبل
            if name != 'مكان غير مسمى' and lat and lon and not is_sent(p_id):
                send_to_telegram(name, ptype, lat, lon)
                save_to_memory(p_id)
                print(f"✅ تم رصد وإرسال: {name}")
                count += 1
                # نرسل 5 أماكن فقط في كل مرة لتجنب الحظر
                if count >= 5: break 
                
        if count == 0:
            print("لم يتم العثور على أماكن جديدة في هذه المحاولة.")
            
    except Exception as e:
        print(f"❌ خطأ في جلب البيانات أو الإرسال: {e}")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("خطأ: تأكد من إضافة السيكريتس")
    else:
        hunt_places()
