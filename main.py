import requests
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID') # تأكد إنه يبدأ بـ @ في الـ Secrets
MEMORY_FILE = "places_memory.txt"
MADINAH_BBOX = "24.15,39.25,24.80,40.00"

def test_connection():
    """هذه الدالة ترسل رسالة بمجرد تشغيل الكود للتأكد أن البوت واصل للقناة"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "✅ رادار طيبة شغال الحين وجاري البحث عن أماكن جديدة..."}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print("✅ البوت نجح في الاتصال بالقناة.")
    else:
        print(f"❌ فشل الاتصال: {r.text}")

def is_sent(pid):
    if not os.path.exists(MEMORY_FILE): return False
    with open(MEMORY_FILE, 'r') as f: return str(pid) in f.read()

def save_to_memory(pid):
    with open(MEMORY_FILE, 'a') as f: f.write(str(pid) + '\n')

def send_to_telegram(name, ptype, lat, lon):
    icon = "☕️" if ptype == "cafe" else "🍽"
    map_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    message = f"{icon} <b>{name}</b> في المدينة المنورة\n📍 {map_link}"
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

def hunt_places():
    # استعلام بسيط جداً للتأكد من جلب أي شيء
    query = f'[out:json];node["amenity"~"cafe|restaurant"]({MADINAH_BBOX});out;'
    url = "https://overpass-api.de/api/interpreter"
    try:
        response = requests.post(url, data={'data': query}).json()
        elements = response.get('elements', [])
        print(f"📊 وجد الرادار {len(elements)} مكان في الخريطة.")
        
        count = 0
        for p in elements:
            name = p.get('tags', {}).get('name')
            if name and not is_sent(p['id']):
                send_to_telegram(name, p.get('tags', {}).get('amenity'), p['lat'], p['lon'])
                save_to_memory(p['id'])
                count += 1
                if count >= 5: break
        print(f"✅ تم إرسال {count} مكان جديد.")
    except Exception as e:
        print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    test_connection() # فحص الاتصال أولاً
    hunt_places()
