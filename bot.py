import os
import threading
import telebot
from telebot import types
from flask import Flask

# Bot Token နှင့် ဆိုင်ရှင် Chat ID
TOKEN = "8974525056:AAFwhj7rUDgG5hJig_zgoZilZPChfDzjW3Q"
ADMIN_CHAT_ID = "6895174491"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render အတွက် Web Server လမ်းကြောင်း (Port ငြိမ်စေရန်)
@app.route('/')
def home():
    return "Htar Wa Ra Bot is running 24/7!"

user_feedback_data = {}

# ၁။ /start ခလုတ် နှိပ်တဲ့အခါ ပြမည့် ပင်မ Menu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📋 ဆိုင်ဝန်ဆောင်မှုများနှင့် ဈေးနှုန်းများ")
    btn2 = types.KeyboardButton("💬 အကြံပြုချက် (Feedback) ပေးမည်")
    btn3 = types.KeyboardButton("📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ် နှင့် လိပ်စာ")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(
        message, 
        "မင်္ဂလာပါခင်ဗျာ 🙏\n'ထာဝရ' မိတ္တူနှင့် ဓါတ်ပုံဆိုင်မှ ကြိုဆိုပါတယ်။ မိတ်ဆွေကို ဘာများ ကူညီပေးရမလဲခင်ဗျာ။", 
        reply_markup=markup
    )

# ၂။ ခလုတ်နှိပ်ချက်အပေါ် မူတည်ပြီး အလိုအလျောက် အဖြေပေးခြင်း
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "📋 ဆိုင်ဝန်ဆောင်မှုများနှင့် ဈေးနှုန်းများ":
        services_text = (
            "📌 **'ထာဝရ' ဆိုင်၏ ဝန်ဆောင်မှုများ:**\n\n"
            "၁။ စာရွက်စာတမ်း မိတ္တူကူးခြင်း / ပရင့်ထုတ်ခြင်း\n"
            "၂။ ဓါတ်ပုံရိုက်ကူးခြင်း / ဓါတ်ပုံထုတ်ခြင်း\n"
            "၃။ မင်္ဂလာဖိတ်စာနှင့် ဖိတ်စာဒီဇိုင်းမျိုးစုံ\n"
            "၄။ လက်ဆောင်ယပ်တောင်ပြုလုပ်ခြင်း\n\n"
            "ဈေးနှုန်းအသေးစိတ်သိလိုပါက ဆိုင်သို့ တိုက်ရိုက်ဆက်သွယ် မေးမြန်းနိုင်ပါသည်။"
        )
        bot.send_message(chat_id, services_text, parse_mode="Markdown")
        
    elif text == "📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ် နှင့် လိပ်စာ":
        map_link = "https://maps.app.goo.gl/4GMaoHEhjMPpWM9y5"
        bot.send_message(
            chat_id, 
            "📞 ဆိုင်ဖုန်းနံပါတ် - 09797523108\n"
            "📍 လိပ်စာ - မြူရုံးလမ်း၊ သံကြိုးတိုင်ရပ်ကွက်၊ ဝါးခယ်မမြို့\n\n"
            "🗺️ [ဆိုင်ကို လာရောက်ရန် ဤနေရာကို နှိပ်ပါ](" + map_link + ")",
            parse_mode="Markdown"
        )
        
    elif text == "💬 အကြံပြုချက် (Feedback) ပေးမည်":
        user_feedback_data[chat_id] = {"step": "waiting_for_feedback"}
        bot.send_message(chat_id, "ကျေးဇူးပြု၍ ဆိုင်ဝန်ဆောင်မှုအပေါ် သင်၏ အကြံပြုချက် သို့မဟုတ် လိုအပ်ချက်များကို ဤချတ်ထဲတွင် ရေးသားပေးပို့ပါ။")
        
    elif chat_id in user_feedback_data and user_feedback_data[chat_id].get("step") == "waiting_for_feedback":
        feedback_text = message.text
        
        # Feedback အသစ်ဝင်လာရင် ဆိုင်ရှင်ဆီကို ပို့ပေးမယ်
        bot.send_message(ADMIN_CHAT_ID, f"📩 ဖောက်သည်ထံမှ Feedback အသစ်:\n\n{feedback_text}\n\nပို့သူ ID: {chat_id}")
        bot.send_message(chat_id, "ကျေးဇူးတင်ပါသည်ခင်ဗျာ 🙏။ မိတ်ဆွေ၏ အကြံပြုချက်ကို ဆိုင်ရှင်ထံသို့ ပေးပို့ပြီးဖြစ်ပါသည်။")
        
        del user_feedback_data[chat_id]
    else:
        bot.reply_to(message, "မိတ်ဆွေ၏ မက်ဆေ့ဂျ်ကို လက်ခံရရှိပါပြီ။ အသေးစိတ်သိလိုပါက အောက်ပါ Menu ခလုတ်များကို အသုံးပြုပေးပါခင်ဗျာ။")

# Bot ကို Background Thread နဲ့ ဖွင့်ခြင်း
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Render ပေးမယ့် Port နဲ့ Flask ဆာဗာကို စတင်ခြင်း
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
