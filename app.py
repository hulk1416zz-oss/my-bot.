import telebot
from telebot import types
import google.generativeai as genai
import os
import threading
import http.server
import socketserver
import time

# --- خادم الويب (عشان السيرفر يبقى صاحي) ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- الإعدادات (مفاتيحك جاهزة) ---
BOT_TOKEN = '8675888280:AAHS50UdimC3vlFvBDPQKBotBBZN8q2U-h4' 
GEMINI_API_KEY = 'AIzaSyAKLQVHIjb9PZyBOr2YmCG6lEIxoutxC3w' 

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# استخدام أسرع نموذج لتجنب أي تأخير
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}

def split_message(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@bot.message_handler(commands=['start'])
def welcome(message):
    user_data[message.chat.id] = {} 
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("English 🇺🇸", callback_data="lang_English"),
               types.InlineKeyboardButton("Spanish 🇪🇸", callback_data="lang_Spanish"),
               types.InlineKeyboardButton("French 🇫🇷", callback_data="lang_French"))
    bot.reply_to(message, "Welcome to AI Novelist Pro! 📚\nPlease select the story language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def choose_length(call):
    user_data[call.message.chat.id]['language'] = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Short Story (~3 Pages)", callback_data="len_Short Story"),
               types.InlineKeyboardButton("Detailed Chapter (~6 Pages)", callback_data="len_Detailed Chapter"))
    bot.edit_message_text("Now, select the length of your text:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('len_'))
def ask_prompt(call):
    user_data[call.message.chat.id]['length'] = call.data.split('_')[1]
    bot.edit_message_text("Great! Now send me your story title or idea:", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def generate_story(message):
    chat_id = message.chat.id
    if chat_id not in user_data or 'language' not in user_data[chat_id]:
        bot.reply_to(message, "Please use /start to configure your story.")
        return

    msg = bot.reply_to(message, "⏳ AI is drafting your masterpiece... please wait.")
    
    try:
        # صياغة الطلب بشكل يضمن جودة عالية جداً للسوق الغربي
        prompt = (f"Write a professional, creative, and highly engaging {user_data[chat_id]['length']} "
                  f"in {user_data[chat_id]['language']} based on: '{message.text}'. "
                  f"Style: Award-winning best-selling author.")
        
        response = model.generate_content(prompt)
        story = response.text
        
        bot.delete_message(chat_id, msg.message_id) 
        for chunk in split_message(story):
            bot.send_message(chat_id, chunk)
            
        # تصفير البيانات للطلب القادم
        user_data[chat_id] = {}
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ System Error: {str(e)[:100]}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
