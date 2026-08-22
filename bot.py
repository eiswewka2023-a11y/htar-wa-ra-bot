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
    btn2 = types.KeyboardButton("💬 အကြံပြုချက် နှင့် အော်ဒါမှာမည်")
    btn3 = types.KeyboardButton("📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ် နှင့် လိပ်စာ")
    markup.add(btn1, btn2, btn3)
    
    bot.reply_to(
        message, 
        "မင်္ဂလာပါခင်ဗျာ 🙏\n'ထာဝရ' မိတ္တူနှင့် ဓါတ်ပုံဆိုင်မှ ကြိုဆိုပါတယ်။ မိတ်ဆွေကို ဘာများ ကူညီပေးရမလဲခင်ဗျာ။", 
        reply_markup=markup
    )

# ၂။ Admin ဘက်က Reply လုပ်ပြီး ပြန်သော စနစ်
@bot.message_handler(func=lambda message: str(message.chat.id) == ADMIN_CHAT_ID and message.reply_to_message)
def admin_reply(message):
    replied_msg = message.reply_to_message.caption or message.reply_to_message.text or ""
    if "ပို့သူ ID:" in replied_msg:
        try:
            target_user_id = replied_msg.split("ပို့သူ ID:")[1].strip().split("\n")[0]
            
            if message.photo:
                photo_id = message.photo[-1].file_id
                caption_text = f"📢 'ထာဝရ' ဆိုင်ရှင်မှ ပြန်ကြားချက်:\n\n{message.caption or ''}"
                bot.send_photo(target_user_id, photo_id, caption=caption_text)
            else:
                bot.send_message(target_user_id, f"📢 'ထာဝရ' ဆိုင်ရှင်မှ ပြန်ကြားချက်:\n\n{message.text}")
                
            bot.reply_to(message, f"✅ User {target_user_id} ဆီသို့ အောင်မြင်စွာ ပို့ပြီးပါပြီ။")
            return
        except Exception as e:
            bot.reply_to(message, f"❌ မပို့နိုင်ခဲ့ပါ။ အကြောင်းရင်း: {e}")
            return

# ၃။ ဖောက်သည်များထံမှ ပုံ (Photo) ပို့လာခြင်းကို လက်ခံခြင်း
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    
    photo_id = message.photo[-1].file_id
    caption = message.caption or "စာတန်းမပါသော ပုံ"
    
    bot.send_photo(
        ADMIN_CHAT_ID, 
        photo_id, 
        caption=f"🖼️ ဖောက်သည်ထံမှ ပုံ/အော်ဒါ ရောက်ရှိပါပြီ!\n\nအသေးစိတ်: {caption}\n\nပို့သူ ID: {chat_id}"
    )
    bot.reply_to(message, "ကျေးဇူးတင်ပါသည်ခင်ဗျာ 🙏။ မိတ်ဆွေ၏ ပုံနှင့် အချက်အလက်များကို ဆိုင်ရှင်ထံသို့ ပေးပို့ပြီးဖြစ်ပါသည်။")

# ၄။ ခလုတ်နှိပ်ချက်အပေါ် မူတည်ပြီး အလိုအလျောက် အဖြေပေးခြင်း နှင့် Order Format ပို့ပေးခြင်း
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
        
    elif text == "💬 အကြံပြုချက် နှင့် အော်ဒါမှာမည်":
        order_format_text = (
            "📝 **အော်ဒါမှာယူရန်/အကြံပြုရန် ဤပုံစံအတိုင်း ဖြည့်စွက် ပို့ပေးပါခင်ဗျာ:**\n\n"
            "၁။ လိုချင်သည့် ဝန်ဆောင်မှု (ဥပမာ- ဓာတ်ပုံ၊ ဖိတ်စာ၊ ပရင့်) -\n"
            "၂။ အရွယ်အစား နှင့် အရေအတွက် -\n"
            "၃။ အထူးမှာကြားလိုသည်များ -\n\n"
            "*(အထက်ပါ အချက်အလက်များနှင့်အတူ လိုအပ်သော ပုံများကိုပါ တွဲ၍ ဤချတ်ထဲသို့ ပို့ပေးနိုင်ပါသည်။)*"
        )
        bot.send_message(chat_id, order_format_text, parse_mode="Markdown")
        user_feedback_data[chat_id] = {"step": "waiting_for_order"}
        
    elif chat_id in user_feedback_data and user_feedback_data[chat_id].get("step") == "waiting_for_order":
        order_text = message.text
        
        bot.send_message(ADMIN_CHAT_ID, f"📩 ဖောက်သည်ထံမှ အော်ဒါ/စာသား အသစ်:\n\n{order_text}\n\nပို့သူ ID: {chat_id}")
        bot.send_message(chat_id, "ကျေးဇူးတင်ပါသည်ခင်ဗျာ 🙏။ မိတ်ဆွေ၏ အချက်အလက်များကို ဆိုင်ရှင်ထံသို့ ပေးပို့ပြီးဖြစ်ပါသည်။ ဆိုင်မှ မကြာမီ ပြန်လည်ဆက်သွယ်ပါမည်။")
        
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
