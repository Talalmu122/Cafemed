import requests
import os

# إحداثيات المدينة المنورة ونطاق البحث (15 كم)
CITY_LOCATION = "24.4673,39.6111" 
RADIUS = "15000"

def send_to_telegram(token, chat_id, name, address, rating, place_id):
    # رابط مباشر للموقع على خرائط جوجل
    maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    
    message = (
        f"<b>☕️ تم رصد كافيه جديد في المدينة!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📍 الاسم:</b> {name}\n"
        f"<b>🗺 الموقع:</b> {address}\n"
        f"<b>⭐ التقييم:</b> {rating if rating else 'لا يوجد تقييم بعد'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار المدينة المنورة - طلال التقني</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "📍 فتح في الخريطة", "url": maps_url}]]}
    }
    requests.post(url, json=payload)

def monitor_cafes():
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    gmaps_key = os.getenv('GMAPS_API_KEY')
    
    # ملف الذاكرة عشان ما يكرر الإرسال
    last_cafes_file = "last_cafes_ids.txt"
    old_ids = set()
    if os.path.exists(last_cafes_file):
        with open(last_cafes_file, "r") as f:
            old_ids = set(f.read().splitlines())

    # البحث عن الأماكن نوع (cafe) باللغة العربية
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={CITY_LOCATION}&radius={RADIUS}&type=cafe&key={gmaps_key}&language=ar"
    
    try:
        response = requests.get(url).json()
        results = response.get('results', [])
        current_ids = set()
        
        for place in results:
            pid = place['place_id']
            current_ids.add(pid)
            if pid not in old_ids:
                name = place['name']
                address = place.get('vicinity', 'المدينة المنورة')
                rating = place.get('rating', 0)
                send_to_telegram(tg_token, chat_id, name, address, rating, pid)

        # حفظ المعرفات للمرة القادمة
        with open(last_cafes_file, "w") as f:
            f.write("\n".join(current_ids))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_cafes()
