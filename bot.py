import os
from flask import Flask, request
import telebot
import google.generativeai as genai

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်တယ်၊ ဥပမာတွေပေးပြီး နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေနဲ့ အဘက်ဘက်က အထောက်အကူပြု အားကိုးရတဲ့သူ ဖြစ်ပါတယ်။
"""

def get_working_model():
    """မိမိ API Key ဖြင့် သုံးနိုင်သော Gemini Model ကို အလိုအလျောက် ရှာဖွေပေးသည့် Function"""
    try:
        available_models = [
            m.name for m in genai.list_models()
            if 'generateContent' in m.supported_generation_methods
        ]
        print(f"Available Models: {available_models}", flush=True)
        
        # ဦးစားပေး Model နာမည်များကို စစ်ဆေးမည်
        for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if preferred in available_models:
                return preferred
                
        if available_models:
            return available_models[0]
    except Exception as e:
        print(f"Model listing error: {e}", flush=True)
        
    return "models/gemini-1.5-flash-latest"

@app.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    data = request.get_json(force=True, silent=True)
    
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        try:
            # အလုပ်လုပ်သော Model နာမည်ကို ယူပြီး Gemini ဆီ စာပို့မည်
            active_model_name = get_working_model()
            model = genai.GenerativeModel(
                model_name=active_model_name,
                system_instruction=SYSTEM_INSTRUCTION
            )
            response = model.generate_content(user_text)
            reply_text = response.text
        except Exception as e:
            print(f"Gemini Error: {e}", flush=True)
            reply_text = f"API Error: {str(e)}"
            
        try:
            bot.send_message(chat_id, reply_text)
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
