import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

# تعطيل تنبيهات شهادات SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# جلب الإعدادات من Secrets
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"
SEEN_ADS_FILE = "seen_habous_ads.json"

def send_telegram(text):
    """دالة إرسال الرسالة مع طباعة الخطأ في حال الفشل"""
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(api_url, json=payload, timeout=15)
        if response.status_code != 200:
            print(f"❌ فشل إرسال تلغرام. كود الخطأ: {response.status_code}")
            print(f"📝 رسالة الخطأ من تلغرام: {response.text}")
        else:
            print("✅ تم إرسال الرسالة إلى تلغرام بنجاح!")
    except Exception as e:
        print(f"❌ خطأ غير متوقع أثناء الاتصال بتلغرام: {str(e)}")

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
    # رسالة فحص أولية للتأكد من الربط
    print("🚀 بدء فحص المنصة...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        seen_ads = load_seen()
        new_ads = []
        
        for a in soup.find_all('a'):
            title = a.get_text(strip=True)
            href = a.get('href')
            
            if href and ("تازة" in title or "جرسيف" in title):
                link = "https://www.habous.gov.ma" + href if href.startswith('/') else href
                
                if link not in seen_ads:
                    print(f"🆕 وجدنا إعلان جديد: {title}")
                    send_telegram(f"🚨 <b>إعلان وقفي جديد!</b>\n\n📌 {title}\n🔗 <a href='{link}'>رابط التفاصيل</a>")
                    new_ads.append(link)
        
        if new_ads:
            save_seen(seen_ads + new_ads)
        else:
            print("ℹ️ لا توجد إعلانات جديدة حالياً.")
            
    except Exception as e:
        print(f"❌ خطأ في فحص الموقع: {e}")

if __name__ == "__main__":
    run()
