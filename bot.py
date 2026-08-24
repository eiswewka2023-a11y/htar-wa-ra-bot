import os
import sys
from flask import Flask, request
import telebot
import google.generativeai as genai

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Gemini Configure
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်တယ်၊ ဥပမာတွေပေးပြီး နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေနဲ့ အဘက်ဘက်က အထောက်အကူပြု အားကိုးရတဲ့သူ ဖြစ်ပါတယ်။
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    data = request.get_json(force=True, silent=True)
    
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        print(f"Received message: {user_text}", flush=True)
        
        try:
            # Gemini ထံ မက်ဆေ့ချ် ပို့ခြင်း
            response = model.generate_content(user_text)
            reply_text = response.text
        except Exception as e:
            # Error တက်ပါက အတိအကျ သိရအောင် Telegram ထဲ တန်းပြမည်
            print(f"Gemini Error: {e}", flush=True)
            reply_text = f"Gemini API Error တက်နေပါသည်: {str(e)}"
            
        try:
            # Telegram ထံ ပြန်ပို့ခြင်း
            bot.send_message(chat_id, reply_text)
            print("Message sent successfully!", flush=True)
        except Exception as e:
            print(f"Telegram Send Error: {e}", flush=True)
            
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://htar-wa-ra-bot.onrender.com/{TOKEN}")
    return "Htar Wa Ra Bot is running smoothly!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
