import requests
import os

# الإحداثيات والنطاق (18 كم) بناءً على الدائرة اللي حددتها
CITY_LOCATION = "24.4673,39.6111" 
RADIUS = "18000" 

def send_to_telegram(token, chat_id, name, address, rating, place_id, ptype):
    # رابط مباشر للموقع على خرائط جوجل
    maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    
    # تحديد الأيقونة حسب النوع
    if ptype == "cafe":
        icon = "☕️"
        label = "كافيه"
    elif ptype == "bakery":
        icon = "🥐"
        label = "مخبز/حلى"
    else:
        icon = "🍴"
        label = "مطعم"
    
    message = (
        f"{icon} <b>رادار طيبة رصد لك: {label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📍 الاسم:</b> {name}\n"
        f"<b>🗺 الموقع:</b> {address}\n"
        f"<b>⭐ التقييم:</b> {rating if rating else 'جديد (لا يوجد تقييم)'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طيبة للجديد - طلال التقني</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": "📍 فتح في الخريطة", "url": maps_url}]]
        }
    }
    requests.post(url, json=payload)

def monitor_city():
    tg_token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    gmaps_key = os.getenv('GMAPS_API_KEY')
    
    # الأنواع التي يبحث عنها الرادار
    types_to_search = ["cafe", "restaurant", "bakery"]

    for ptype in types_to_search:
        # طلب البيانات من جوجل ماب
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={CITY_LOCATION}&radius={RADIUS}&type={ptype}&key={gmaps_key}&language=ar"
        
        try:
            response = requests.get(url).json()
            results = response.get('results', [])
            
            # بنرسل أول 3 نتائج فقط من كل نوع عشان ما يمتلي الشات فجأة
            for place in results[:3]:
                name = place['name']
                address = place.get('vicinity', 'المدينة المنورة')
                rating = place.get('rating', 0)
                pid = place['place_id']
                send_to_telegram(tg_token, chat_id, name, address, rating, pid, ptype)
        except Exception as e:
            print(f"خطأ في البحث عن {ptype}: {e}")

if __name__ == "__main__":
    monitor_city()
