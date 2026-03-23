import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"

def send_msg(text):
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    requests.post(api_url, data=payload, timeout=10)

def check():
    # رسالة لتأكيد أن السكريبت اشتغل بنجاح (يمكنك حذفها لاحقاً)
    send_msg("🔄 بدأت عملية الفحص الآن...")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # تجاوز حماية الشهادة وتمديد وقت الانتظار
        res = requests.get(URL, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_something = False
        for a in soup.find_all('a'):
            txt = a.get_text()
            link = a.get('href')
            if link and ("تازة" in txt or "جرسيف" in txt):
                full_link = "https://www.habous.gov.ma" + link if link.startswith('/') else link
                send_msg(f"✅ وجدنا إعلان! \n📌 {txt} \n🔗 {full_link}")
                found_something = True
        
        if not found_something:
            send_msg("ℹ️ تم الفحص بنجاح، لكن لا توجد إعلانات لـ 'تازة' أو 'جرسيف' حالياً.")
            
    except Exception as e:
        send_msg(f"❌ حدث خطأ أثناء الفحص: {str(e)}")

if __name__ == "__main__":
    check()
