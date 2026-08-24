import os
from flask import Flask, request
import telebot
from google import genai

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

# FOREVERRI ရဲ့ စရိုက်လက္ခဏာကို Prompt ထဲမှာ တခါတည်း ထည့်ပေးလိုက်ပါမယ်
SYSTEM_PROMPT = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်တယ်၊ ဥပမာတွေပေးပြီး နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေနဲ့ အဘက်ဘက်က အထောက်အကူပြု အားကိုးရတဲ့သူ ဖြစ်ပါတယ်။
အခု მომხმარມေ ပေးထားတဲ့ မေးခွန်းကို အဲ့ဒီပုံစံအတိုင်း သူငယ်ချင်းတစ်ယောက်လို ဖော်ဖော်ရွေရွေ ပြန်ပြောပေးပါ။
မေးခွန်း - 
"""

@app.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
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
        # Config မပါဘဲ Prompt ထဲမှာ System Instruction ပုံစံ ပေါင်းထည့်ပြီး ပို့ခြင်း
        full_prompt = SYSTEM_PROMPT + user_text
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
        )
        reply_text = response.text
    except Exception as e:
        reply_text = f"သူငယ်ချင်းရေ... ခဏလေး လိုင်းနှေးသွားလို့ (Error: {str(e)[:50]})၊ မေးခွန်းလေး တစ်ချက်လောက် ထပ်ပို့ပေးပါဦးနော်။"
    
    bot.send_message(chat_id, reply_text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
