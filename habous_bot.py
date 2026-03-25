import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# جلب البيانات
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def debug_telegram():
    print(f"--- فحص الاتصال بتلجرام ---")
    if not TOKEN or not CHAT_ID:
        print("❌ خطأ: لم يتم العثور على TOKEN أو CHAT_ID في Secrets!")
        return

    test_url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        # فحص هل التوكن صحيح أصلاً
        res_me = requests.get(test_url, timeout=10)
        print(f"🔍 فحص التوكن: {res_me.text}")
        
        # محاولة إرسال رسالة تجريبية
        send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": "🔔 تجربة نظام التنبيهات: الربط يعمل بنجاح!"}
        res_send = requests.post(send_url, data=payload, timeout=10)
        
        if res_send.status_code == 200:
            print("✅ نجاح! الرسالة وصلت لهاتفك.")
        else:
            print(f"❌ فشل الإرسال! رد تلجرام: {res_send.text}")
            print("💡 نصيحة: تأكد أنك أرسلت /start للبوت في تلجرام.")
            
    except Exception as e:
        print(f"❌ خطأ تقني: {e}")

if __name__ == "__main__":
    debug_telegram()