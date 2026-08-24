import os
from flask import Flask, request
import telebot
import google.generativeai as genai

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# အသေချာဆုံး Google Generative AI (Stable Version) ကို ချိတ်ဆက်ခြင်း
genai.configure(api_key=GEMINI_API_KEY)

# FOREVERRI ရဲ့ စရိုက်လက္ခဏာ
SYSTEM_INSTRUCTION = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်တယ်၊ ဥပမာတွေပေးပြီး နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေနဲ့ အဘက်ဘက်က အထောက်အကူပြု အားကိုးရတဲ့သူ ဖြစ်ပါတယ်။
"""

# Model ကို ကြိုတင်ပြင်ဆင်ထားခြင်း
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    try:
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Webhook Error: {e}")
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://htar-wa-ra-bot.onrender.com/{TOKEN}")
    return "Htar Wa Ra Bot is running smoothly!", 200

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id
    
    try:
        # Gemini ဆီက အဖြေတောင်းခြင်း
        response = model.generate_content(user_text)
        reply_text = response.text
    except Exception as e:
        # Error တက်ရင် Render Log မှာ ဘာကြောင့်လဲဆိုတာ အတိအကျ ပေါ်အောင်လုပ်ထားသည်
        print(f"Gemini API Error: {e}")
        reply_text = "သူငယ်ချင်းရေ... ခဏလေး လိုင်းနှေးသွားလို့၊ မေးခွန်းလေး တစ်ချက်လောက် ထပ်ပို့ပေးပါဦးနော်။"
    
    try:
        # အဖြေကို Telegram သို့ ပြန်ပို့ခြင်း
        bot.send_message(chat_id, reply_text)
    except Exception as e:
        print(f"Telegram Send Error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
