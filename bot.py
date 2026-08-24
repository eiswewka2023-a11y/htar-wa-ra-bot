import os
from flask import Flask, request
import telebot
from google import genai
from google.genai import types

# Token နဲ့ API Key တွေကို Environment Variables ကနေ ယူပါတယ်
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Google GenAI Client အသစ်ကို ချိတ်ဆက်ခြင်း
client = genai.Client(api_key=GEMINI_API_KEY)

# FOREVERRI ရဲ့ စရိုက်လက္ခဏာနဲ့ ဆိုင်အချက်အလက်များကို သတ်မှတ်ပေးခြင်း
SYSTEM_INSTRUCTION = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108, TikTok - https://www.tiktok.com/@sara.eiswe?_r=1&_t=ZS-995a5DBYIlg) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်တယ်၊ ဥပမာတွေပေးပြီး နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေနဲ့ အဘက်ဘက်က အထောက်အကူပြု အားကိုးရတဲ့သူ ဖြစ်ပါတယ်။
"""

@app.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    # Webhook ကို Telegram နဲ့ ချိတ်ရန်
    bot.remove_webhook()
    bot.set_webhook(url=f"https://htar-wa-ra-bot.onrender.com/{TOKEN}")
    return "Htar Wa Ra Bot is running smoothly!", 200

# Telegram ကနေ စာပို့လာရင် ဖမ်းယူပြီး Gemini ဆီ ပို့မယ့် Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    try:
        # Gemini API အသစ်သုံးပြီး အဖြေထုတ်ခြင်း
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            ),
        )
        reply_text = response.text
    except Exception as e:
        reply_text = "သူငယ်ချင်းရေ... ခဏလေး လိုင်းခဏနှေးသွားလို့ ထင်တယ်၊ မေးခွန်းလေး တစ်ချက်လောက် ထပ်ပို့ပေးပါဦးနော်။"
    
    bot.send_message(chat_id, reply_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
