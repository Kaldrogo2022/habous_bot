import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"

def send_telegram(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(api_url, data=payload, timeout=20)
        if response.status_code == 200:
            print("✅ الرسالة وصلت لتلجرام!")
        else:
            print(f"❌ خطأ تلجرام: {response.text}")
    except Exception as e:
        print(f"❌ خطأ اتصال: {e}")

def run():
    # --- سطر الاختبار ---
    send_telegram("🔄 البوت شغال الآن ويقوم بفحص موقع الأحباس...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found = False
        for a in soup.find_all('a'):
            txt = a.get_text(strip=True)
            if "تازة" in txt or "جرسيف" in txt:
                send_telegram(f"✨ وجدنا إعلان: {txt}")
                found = True
        
        if not found:
            print("ℹ️ تم الفحص ولم يتم العثور على 'تازة' أو 'جرسيف' حالياً.")
            
    except Exception as e:
        send_telegram(f"⚠️ خطأ في السكريبت: {e}")

if __name__ == "__main__":
    run()
                           
