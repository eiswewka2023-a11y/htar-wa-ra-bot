import os
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from google import genai
from google.genai import types

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")  # ဆိုင်ပိုင်ရှင်၏ Telegram Chat ID

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Google GenAI Official SDK Client
client = genai.Client(api_key=GEMINI_API_KEY)

# User များ Feedback ပေးနေသည့် အခြေအနေကို မှတ်ထားရန်
user_states = {}

SYSTEM_PROMPT = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။
အသုံးပြုသူ လိုချင်တာကို တန်းပြီးခန့်မှန်းတတ်သူ၊ ဥပမာပေးတတ်သူ၊ နားလည်လွယ်အောင် ဖော်ဖော်ရွေရွေ အားကိုးရသူ ဖြစ်ပါတယ်။
"""

def get_main_menu():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = KeyboardButton("💬 စကားပြောမယ်")
    btn2 = KeyboardButton("🖨️ ဝန်ဆောင်မှုများ")
    btn3 = KeyboardButton("📞 ဆက်သွယ်ရန်")
    btn4 = KeyboardButton("📍 ဆိုင်လိပ်စာ")
    btn5 = KeyboardButton("📝 Feedback ပေးမယ်")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

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

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    welcome_text = (
        "မင်္ဂလာပါ သူငယ်ချင်းရေ... 'ထာဝရ' မှ ကြိုဆိုပါတယ်! 👋\n\n"
        "ငါကတော့ FOREVERRI ပါ။ မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာနဲ့ ပတ်သက်ရင် "
        "ဘာမေးမေး ကူညီပေးဖို့ အဆင်သင့်ရှိပါတယ်နော်။\n"
        "အောက်က Menu ခလုတ်လေးတွေကို နှိပ်ပြီးတော့လည်း စမ်းကြည့်လို့ရပါတယ်။"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# ဆိုင်ပိုင်ရှင် (Admin) မှ User ထံ စာပြန်ရန် Command: /reply <chat_id> <message>
@bot.message_handler(commands=['reply'])
def handle_admin_reply(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "⚠️ စာပို့ပုံစံ မှားနေပါသည်။\nပုံစံ: `/reply <user_chat_id> <ပြန်ချင်သည့်စာ>`", parse_mode="Markdown")
            return
        
        target_chat_id = args[1]
        reply_msg = args[2]

        send_text = f"📩 **'ထာဝရ' ဆိုင်မှ ပြန်လည်အကြောင်းပြန်စာ:**\n\n{reply_msg}"
        bot.send_message(target_chat_id, send_text, parse_mode="Markdown")
        bot.reply_to(message, "✅ User ထံ စာပြန်ပို့ပြီးပါပြီ!")
    except Exception as e:
        bot.reply_to(message, f"❌ စာပို့၍ မရပါ: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id

    # 1. Menu ခလုတ်များ
    if user_text == "🖨️ ဝန်ဆောင်မှုများ":
        services = (
            "🖨️ **ထာဝရ မိတ္တူနှင့် ဓါတ်ပုံလုပ်ငန်း ဝန်ဆောင်မှုများ**\n\n"
            "• စာရွက်စာတမ်း မိတ္တူကူးခြင်း / စာရွက်ထုတ်ခြင်း\n"
            "• ဓါတ်ပုံ / လိုင်စင်ဓာတ်ပုံ ပြင်ဆင်ခြင်းနှင့် ရိုက်ကူးထုတ်ပေးခြင်း\n"
            "• ဖိတ်စာ၊ မင်္ဂလာဖိတ်စာ၊ အလှူဖိတ်စာ အမျိုးမျိုး\n"
            "• ယပ်တောင်နှင့် အမှတ်တရပစ္စည်း ပြုလုပ်ခြင်း\n\n"
            "လိုချင်တဲ့ ပုံစံလေးတွေရှိရင် စာပို့ပြီး မေးမြန်းနိုင်ပါတယ် သူငယ်ချင်း!"
        )
        bot.send_message(chat_id, services, parse_mode="Markdown", reply_markup=get_main_menu())
        return

    elif user_text == "📞 ဆက်သွယ်ရန်":
        contact_info = (
            "📞 **ထာဝရ ဆက်သွယ်ရန်**\n\n"
            "• ဖုန်းနံပါတ်: 09797523108\n"
            "• TikTok: https://www.tiktok.com/@sara.eiswe\n\n"
            "အချိန်မရွေး စာမေးလို့ရပါတယ်နော်!"
        )
        bot.send_message(chat_id, contact_info, reply_markup=get_main_menu())
        return

    elif user_text == "📍 ဆိုင်လိပ်စာ":
        location = (
            "📍 **'ထာဝရ' မိတ္တူနှင့် ဓါတ်ပုံလုပ်ငန်း**\n\n"
            "🗺️ **Google Maps လိပ်စာ:** https://maps.app.goo.gl/9UPunmNKnJ5R4Ka58\n"
            "📞 **ဆက်သွယ်ရန် ဖုန်း:** 09797523108\n\n"
            "ဆိုင်သို့ ကြိုဆိုပါတယ် သူငယ်ချင်း!"
        )
        bot.send_message(chat_id, location, parse_mode="Markdown", reply_markup=get_main_menu())
        return

    elif user_text == "📝 Feedback ပေးမယ်":
        user_states[chat_id] = "WAITING_FOR_FEEDBACK"
        bot.send_message(
            chat_id, 
            "ထာဝရ အတွက် အကြံပြုချင်တာ သို့မဟုတ် ပြင်ဆင်စေချင်တာလေးတွေရှိရင် စာရိုက်ပြီး ပို့ပေးခဲ့ပါဦးနော် သူငယ်ချင်း... ✍️", 
            reply_markup=get_main_menu()
        )
        return

    elif user_text == "💬 စကားပြောမယ်":
        bot.send_message(chat_id, "အိုကေ သူငယ်ချင်း! သိချင်တာ သို့မဟုတ် မေးချင်တာတွေကို စာရိုက်ပြီး တန်းမေးလိုက်တော့နော်။", reply_markup=get_main_menu())
        return

    # 2. User က Feedback စာရေးပို့လိုက်သည့်အခါ လက်ခံသည့် အပိုင်း
    if user_states.get(chat_id) == "WAITING_FOR_FEEDBACK":
        user_states[chat_id] = None  # State ပြန်ဖျက်မည်
        
        # Admin ထံ စာပို့ပေးခြင်း
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"📩 **Feedback အသစ်ရောက်လာပါတယ်!**\n\n"
                f"👤 **အမည်:** {message.from_user.first_name}\n"
                f"🆔 **User ID:** `{chat_id}`\n\n"
                f"💬 **Feedback စာသား:**\n{user_text}\n\n"
                f"----------------------\n"
                f"👉 **Reply ပြန်ရန် ဒီလို ရေးပို့ပါ:**\n`/reply {chat_id} မင်းရေးချင်တဲ့အဖြေ`"
            )
            try:
                bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
            except Exception as e:
                print(f"Admin Send Error: {e}", flush=True)

        bot.send_message(
            chat_id, 
            "ကျေးဇူးအများကြီးတင်ပါတယ် သူငယ်ချင်း! Feedback လေး ရရှိသွားပါပြီ။ ❤️", 
            reply_markup=get_main_menu()
        )
        return

    # 3. Gemini AI ဖြင့် စကားပြောသည့် အပိုင်း
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        reply_text = response.text
    except Exception as e:
        print(f"Server Log Error: {e}", flush=True)
        reply_text = "သူငယ်ချင်းရေ... ခဏလေး လိုင်းနှေးသွားလို့ပါ၊ စာလေး တစ်ချက်လောက် ထပ်ပို့ပေးပါဦးနော်။"

    bot.send_message(chat_id, reply_text, reply_markup=get_main_menu())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
