import requests
import os

# إحداثيات المدينة المنورة ونطاق البحث (15 كم)
CITY_LOCATION = "24.4673,39.6111" 
RADIUS = "15000"

def send_to_telegram(token, chat_id, name, address, rating, place_id, ptype):
    maps_url = f"https://www.google.com/maps/search/?api=1&query=Google&query_place_id={place_id}"
    
    # تحديد الأيقونة حسب نوع المكان
    icon = "☕️" if ptype == "cafe" else "🍴"
    
    message = (
        f"{icon} <b>تم رصد موقع جديد في المدينة!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📍 الاسم:</b> {name}\n"
        f"<b>🗺 الموقع:</b> {address}\n"
        f"<b>⭐️ التقييم:</b> {rating if rating else 'لا يوجد تقييم (افتتاح جديد! 😍)'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار المدينة المنورة - طلال التقني</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "📍 افتح في الخريطة", "url": maps_url}]]}
    }
    requests.post(url, json=payload)

def monitor_city():
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    gmaps_key = os.getenv('GMAPS_API_KEY')
    
    last_ids_file = "last_places_ids.txt"
    old_ids = set()
    if os.path.exists(last_ids_file):
        with open(last_ids_file, "r") as f:
            old_ids = set(f.read().splitlines())

    # أنواع الأماكن اللي نبي نصيدها
    types_to_search = ["cafe", "restaurant", "bakery"]
    current_ids = set()

    for ptype in types_to_search:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={CITY_LOCATION}&radius={RADIUS}&type={ptype}&key={gmaps_key}&language=ar"
        try:
            response = requests.get(url).json()
            results = response.get('results', [])
            
            for place in results:
                pid = place['place_id']
                current_ids.add(pid)
                if pid not in old_ids:
                    name = place['name']
                    address = place.get('vicinity', 'المدينة المنورة')
                    rating = place.get('rating', 0)
                    send_to_telegram(tg_token, chat_id, name, address, rating, pid, ptype)
        except:
            continue

    with open(last_ids_file, "w") as f:
        f.write("\n".join(current_ids))

if __name__ == "__main__":
    monitor_city()
