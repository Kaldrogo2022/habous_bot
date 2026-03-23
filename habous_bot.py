import os
import requests
from bs4 import BeautifulSoup
import json
import urllib3

# تعطيل تنبيهات شهادات SSL غير الموثوقة
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

TARGET_URL = "https://www.habous.gov.ma/component/mtree/السمسرات-الوقفية/الكراء.html"
SEEN_ADS_FILE = "seen_habous_ads.json"

def load_seen_ads():
    if os.path.exists(SEEN_ADS_FILE):
        try:
            with open(SEEN_ADS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return []
    return []

def save_seen_ads(seen_ads):
    with open(SEEN_ADS_FILE, "w", encoding="utf-8") as file:
        json.dump(seen_ads, file, ensure_ascii=False, indent=4)

def send_telegram_alert(title, link):
    message = f"🚨 <b>إعلان كراء وقفي جديد!</b>\n\n📌 <b>المنطقة:</b> {title}\n🔗 <b>التفاصيل:</b> <a href='{link}'>اضغط هنا</a>"
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(api_url, data=payload, timeout=10)
    except:
        pass

def check_habous_platform():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # إضافة verify=False لتجاوز خطأ الشهادة
        response = requests.get(TARGET_URL, headers=headers, timeout=20, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        seen_ads = load_seen_ads()
        new_ads_found = False
        
        all_links = soup.find_all('a')
        for a_tag in all_links:
            title = a_tag.get_text(strip=True)
            href = a_tag.get('href')
            if href and ("تازة" in title or "جرسيف" in title):
                full_link = "https://www.habous.gov.ma" + href if href.startswith('/') else href
                if full_link not in seen_ads:
                    send_telegram_alert(title, full_link)
                    seen_ads.append(full_link)
                    new_ads_found = True
        
        if new_ads_found:
            save_seen_ads(seen_ads)
        elif not os.path.exists(SEEN_ADS_FILE):
            save_seen_ads([]) # إنشاء ملف فارغ إذا لم يوجد لتجنب خطأ Git
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_habous_platform()
                         
