import os
from flask import Flask, request
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from google import genai
from google.genai import types

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

client = genai.Client(api_key=GEMINI_API_KEY)

# User တစ်ယောက်ချင်းစီ၏ စကားပြော狀態 (State) ကို မှတ်ထားရန်
user_states = {}

SYSTEM_PROMPT = """
မင်းနာမည်က FOREVERRI ဖြစ်ပြီး ကောင်လေးတစ်ယောက် ဖြစ်ပါတယ်။ 
မင်းက "ထာဝရ" မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာ၊ ယပ်တောင်လုပ်ငန်း (ဖုန်းနံပါတ် - 09797523108) မှာ အလုပ်လုပ်နေတဲ့ သူငယ်ချင်း/မိတ်ဆွေတစ်ယောက်လို စကားပြောပါတယ်။
စာနဲ့ ဓါတ်ပုံထုတ်တာတွေ၊ ဖိတ်စာနဲ့ ပတ်သက်လာရင် ကျွမ်းကျင်သူတစ်ယောက်လို အကြံပေးတတ်တယ်၊ ပြင်ဆင်ပေးတတ်တယ်။

အရေးကြီးသော စည်းကမ်းချက်:
• စာပြန်သည့်အခါ အရှည်ကြီး မရေးရပါ။
• လိုရင်းတိုရှင်း တိုတိုတုပ်တုပ်ပဲ စာကြောင်း ၂ ကြောင်း သို့မဟုတ် ၃ ကြောင်းထက် မပိုဘဲ ရင်းနှီးဖော်ရွေစွာ ပြန်ဖြေပေးပါ။
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

def generate_ai_response(prompt_text):
    models_to_try = ['gemini-3.6-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
    last_error = ""

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_error = str(e)
            print(f"Model {model_name} Error: {e}", flush=True)

    return f"⚠️ Gemini API Error:\n{last_error}\n\n👉 GEMINI_API_KEY မှန်မမှန် Render Environment Variables မှာ စစ်ဆေးပေးပါဦး။"

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
    user_states[message.chat.id] = None  # State ပြန်ဖျက်မည်
    welcome_text = (
        "မင်္ဂလာပါ သူငယ်ချင်းရေ... 'ထာဝရ' မှ ကြိုဆိုပါတယ်! 👋\n\n"
        "ငါကတော့ FOREVERRI ပါ။ မိတ္တူ၊ ဓါတ်ပုံ၊ ဖိတ်စာနဲ့ ပတ်သက်ရင် "
        "ဘာမေးမေး ကူညီပေးဖို့ အဆင်သင့်ရှိပါတယ်နော်။\n"
        "ပုံတွေ/စာရွက်စာတမ်းတွေ ပို့ချင်ရင်လည်း တိုက်ရိုက် ပို့ပေးလို့ရပါတယ်!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

# Admin မှ Customer ထံ စာပြန်ပေးခြင်း
@bot.message_handler(commands=['reply'])
def handle_admin_reply(message):
    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            bot.reply_to(message, "⚠️ စာပို့ပုံစံ မှားနေပါသည်။\nပုံစံ: `/reply <user_chat_id> <ပြန်ချင်သည့်စာ>`", parse_mode="Markdown")
            return
        
        target_chat_id = str(args[1]).strip()
        reply_msg = args[2]

        # Customer ရဲ့ State ကို ဆိုင်နှင့် တိုက်ရိုက် စကားပြောနေသည့်အဆင့်သို့ ပြောင်းပါမည်
        user_states[int(target_chat_id)] = "CHAT_WITH_ADMIN"

        send_text = (
            f"📩 **'ထာဝရ' ဆိုင်မှ ပြန်လည်အကြောင်းပြန်စာ:**\n\n{reply_msg}\n\n"
            f"💡 _(ဆိုင်သို့ ဆက်လက် စာပြန်လိုပါက ဒီထဲမှာ စာရိုက်၍ တိုက်ရိုက် ပို့နိုင်ပါတယ်)_"
        )
        bot.send_message(target_chat_id, send_text, parse_mode="Markdown", reply_markup=get_main_menu())
        bot.reply_to(message, f"✅ User ({target_chat_id}) ထံ စာပြန်ပို့ပြီးပါပြီ!")
    except Exception as e:
        bot.reply_to(message, f"❌ စာပို့၍ မရပါ: {str(e)}")

# Customer ထံမှ ဓါတ်ပုံ ရောက်ရှိလာပါက Handling
@bot.message_handler(content_types=['photo'])
def handle_incoming_photo(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    caption = message.caption if message.caption else "စာသားမပါပါ"
    photo_file_id = message.photo[-1].file_id

    if ADMIN_CHAT_ID:
        admin_msg = (
            f"📸 **ဓါတ်ပုံအသစ် ရောက်ရှိလာပါတယ်!**\n\n"
            f"👤 **ပို့သူ:** {user_name}\n"
            f"🆔 **User ID:** `{chat_id}`\n"
            f"📝 **Caption:** {caption}\n\n"
            f"----------------------\n"
            f"👉 **Reply ပြန်ရန်:**\n`/reply {chat_id} စာပြန်လိုသည့်စာ`"
        )
        try:
            bot.send_photo(ADMIN_CHAT_ID, photo_file_id, caption=admin_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Admin Photo Send Error: {e}", flush=True)

    bot.send_message(
        chat_id, 
        "ဓါတ်ပုံလေး ရရှိပါတယ် သူငယ်ချင်း! 📸 'ထာဝရ' မှ စစ်ဆေးပြီး အမြန်ဆုံး ပြန်လည် အကြောင်းပြန်ပေးပါမယ်နော်။", 
        reply_markup=get_main_menu()
    )

# Customer စာပို့သမျှ ပင်မ Handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_text = message.text
    chat_id = message.chat.id

    # 1. Menu ခလုတ်များ နှိပ်ပါက State အဟောင်းများကို ဖျက်မည်
    if user_text in ["🖨️ ဝန်ဆောင်မှုများ", "📞 ဆက်သွယ်ရန်", "📍 ဆိုင်လိပ်စာ", "💬 စကားပြောမယ်", "📝 Feedback ပေးမယ်"]:
        user_states[chat_id] = None

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

    # 2. Customer သည် Admin ၏ စာကို တိုက်ရိုက် စာပြန်နေသည့် အခြေအနေ (Follow-up Chat)
    if user_states.get(chat_id) == "CHAT_WITH_ADMIN":
        if ADMIN_CHAT_ID:
            admin_msg = (
                f"💬 **Customer ထံမှ တိုက်ရိုက် ပြန်လည် ပို့လိုက်သောစာ:**\n\n"
                f"👤 **အမည်:** {message.from_user.first_name}\n"
                f"🆔 **User ID:** `{chat_id}`\n\n"
                f"📝 **စာသား:**\n{user_text}\n\n"
                f"----------------------\n"
                f"👉 **ထပ်မံ Reply ပြန်ရန်:**\n`/reply {chat_id} မင်းရေးချင်တဲ့အဖြေ`"
            )
            try:
                bot.send_message(ADMIN_CHAT_ID, admin_msg, parse_mode="Markdown")
            except Exception as e:
                print(f"Admin Relay Error: {e}", flush=True)

        bot.send_message(chat_id, "ဆိုင်သို့ စာပို့လိုက်ပါပြီ သူငယ်ချင်း! ဆိုင်မှ အကြောင်းပြန်ပေးပါလိမ့်မည်။ ❤️", reply_markup=get_main_menu())
        return

    # 3. Feedback ပို့သည့် အခြေအနေ
    if user_states.get(chat_id) == "WAITING_FOR_FEEDBACK":
        user_states[chat_id] = None
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

    # 4. Gemini AI ဖြင့် ပုံမှန် စကားပြောသည့် အပိုင်း
    reply_text = generate_ai_response(user_text)
    bot.send_message(chat_id, reply_text, reply_markup=get_main_menu())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
