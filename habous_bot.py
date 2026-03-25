import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

# تعطيل تنبيهات شهادات SSL لتفادي أخطاء الاتصال بالموقع
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# جلب الإعدادات باستخدام التسمية الخاصة بك في GitHub Secrets
TOKEN = os.environ.get('TELEGRAM_TOKEN')  # تم التعديل ليطابق تسميتك
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"
SEEN_ADS_FILE = "seen_habous_ads.json"

def send_telegram(text):
    """إرسال التنبيه إلى تلجرام مع طباعة النتيجة في سجلات GitHub"""
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(api_url, json=payload, timeout=20)
        if response.status_code == 200:
            print("✅ نجاح: تم إرسال الرسالة إلى تلجرام.")
        else:
            print(f"❌ فشل: رد تلجرام هو {response.text}")
    except Exception as e:
        print(f"❌ خطأ اتصال: {e}")

def run():
    print("🔍 جاري فحص منصة الأحباس...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # الاتصال بالموقع وتجاوز فحص الشهادة
        res = requests.get(URL, headers=headers, verify=False, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # تحميل الإعلانات التي سبق إرسالها
        seen = []
        if os.path.exists(SEEN_ADS_FILE):
            with open(SEEN_ADS_FILE, "r", encoding="utf-8") as f:
                try: seen = json.load(f)
                except: seen = []

        new_links = []
        for a in soup.find_all('a'):
            txt = a.get_text(strip=True)
            href = a.get('href')
            
            # البحث عن الكلمات المفتاحية
            if href and ("تازة" in txt or "جرسيف" in txt):
                link = "https://www.habous.gov.ma" + href if href.startswith('/') else href
                
                if link not in seen:
                    print(f"✨ اكتشاف إعلان جديد: {txt}")
                    msg = f"🚨 <b>إعلان وقفي جديد!</b>\n\n📌 {txt}\n🔗 <a href='{link}'>رابط التفاصيل</a>"
                    send_telegram(msg)
                    new_links.append(link)

        # حفظ الروابط الجديدة لمنع تكرار الإرسال
        if new_links:
            with open(SEEN_ADS_FILE, "w", encoding="utf-8") as f:
                json.dump(seen + new_links, f, ensure_ascii=False, indent=4)
        else:
            print("ℹ️ لا توجد إعلانات جديدة لـ 'تازة' أو 'جرسيف'.")

    except Exception as e:
        print(f"❌ خطأ أثناء تشغيل السكريبت: {e}")

if __name__ == "__main__":
    run()
