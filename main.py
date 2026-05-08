import requests
import os

def test_radar():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    gmaps_key = os.getenv('GMAPS_API_KEY')
    
    # 1. تجربة إرسال رسالة بسيطة للتليجرام
    test_msg = "🔔 فحص الاتصال: إذا وصلت هذه الرسالة فالبوت سليم!"
    tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
    r_tg = requests.post(tg_url, json={"chat_id": chat_id, "text": test_msg})
    
    if r_tg.status_code == 200:
        print("✅ التليجرام سليم والرسالة وصلت!")
    else:
        print(f"❌ خطأ في التليجرام: {r_tg.text}")

    # 2. تجربة جلب بيانات من جوجل ماب (كافيه واحد فقط)
    # إحداثيات قريبة جداً من الحرم
    loc = "24.4673,39.6111"
    g_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={loc}&radius=5000&type=cafe&key={gmaps_key}"
    r_g = requests.get(g_url).json()
    
    status = r_g.get('status')
    if status == "OK":
        print(f"✅ جوجل ماب سليم! وجدنا {len(r_g.get('results'))} كافيه.")
    else:
        print(f"❌ خطأ من جوجل ماب: {status}")
        if status == "REQUEST_DENIED":
            print("السبب: مفتاح API غير مفعل أو Places API معطلة.")

if __name__ == "__main__":
    test_radar()
