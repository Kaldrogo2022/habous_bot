import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

# تعطيل تنبيهات الأمان للموقع
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# الإعدادات الخاصة بك
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"
SEEN_ADS_FILE = "seen_habous_ads.json"

def send_telegram(text):
    """إرسال رسالة مفصلة مع رابط قابل للضغط"""
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(api_url, data=payload, timeout=20)
        print("✅ تم إرسال التفاصيل بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")

def load_seen():
    if os.path.exists(SEEN_ADS_FILE):
        with open(SEEN_ADS_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_seen(data):
    with open(SEEN_ADS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def run():
    print("🔍 جاري فحص الإعلانات بالتفصيل...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(URL, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        seen_ads = load_seen()
        new_links = []
        
        # البحث عن الروابط التي تحتوي على نصوص المدن المطلوبة
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            
            if href and ("تازة" in title or "جرسيف" in title):
                # بناء الرابط الكامل
                full_link = "https://www.habous.gov.ma" + href if href.startswith('/') else href
                
                # التحقق إذا كان الإعلان جديداً
                if full_link not in seen_ads:
                    print(f"🆕 اكتشاف إعلان: {title}")
                    
                    # صياغة الرسالة بشكل احترافي
                    message = (
                        f"🔔 <b>إعلان وقفي جديد تم رصده!</b>\n\n"
                        f"📍 <b>المنطقة/الموضوع:</b> {title}\n"
                        f"🔗 <b>رابط التفاصيل:</b> <a href='{full_link}'>اضغط هنا للمعاينة</a>\n\n"
                        f"🕒 <i>تم الفحص آلياً بنجاح.</i>"
                    )
                    
                    send_telegram(message)
                    new_links.append(full_link)

        if new_links:
            save_seen(seen_ads + new_links)
            print(f"✅ تم حفظ {len(new_links)} إعلان جديد.")
        else:
            print("ℹ️ لا توجد إعلانات جديدة حالياً تخص تازة أو جرسيف.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء جلب البيانات: {e}")

if __name__ == "__main__":
    run()
    
