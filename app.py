import telebot
from telebot import types
import requests
import os
import threading
import http.server
import socketserver
import time

# --- خادم الويب (عشان السيرفر ما يطفي) ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- الإعدادات ---
BOT_TOKEN = '8675888280:AAHS50UdimC3vlFvBDPQKBotBBZN8q2U-h4'
GROQ_API_KEY = 'Gsk_csE1OleO06dttE0o05J2WGdyb3FYQzHo5cv0dlRmUIBwEYtNvH57'

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def split_message(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def generate_groq_story(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192", # تم تغيير الموديل للأكثر استقراراً
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    res_json = response.json()
    
    # التأكد من نجاح الطلب
    if 'choices' in res_json:
        return res_json['choices'][0]['message']['content']
    else:
        # إذا فيه خطأ، يطبع لنا بالضبط وش المشكلة
        return f"⚠️ API Response: {str(res_json)}"

@bot.message_handler(commands=['start'])
def welcome(message):
    user_data[message.chat.id] = {}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("English 🇺🇸", callback_data="lang_English"),
               types.InlineKeyboardButton("Spanish 🇪🇸", callback_data="lang_Spanish"),
               types.InlineKeyboardButton("French 🇫🇷", callback_data="lang_French"))
    bot.reply_to(message, "Welcome to AI Novelist Pro! 📚\nPlease select the language:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def choose_length(call):
    user_data[call.message.chat.id]['language'] = call.data.split('_')[1]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Short Story", callback_data="len_Short Story"),
               types.InlineKeyboardButton("Detailed Chapter", callback_data="len_Detailed Chapter"))
    bot.edit_message_text("Select length:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('len_'))
def ask_prompt(call):
    user_data[call.message.chat.id]['length'] = call.data.split('_')[1]
    bot.edit_message_text("Send me your story title or idea:", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_story(message):
    chat_id = message.chat.id
    if chat_id not in user_data or 'language' not in user_data[chat_id]:
        bot.reply_to(message, "Please use /start first.")
        return

    msg = bot.reply_to(message, "⏳ AI is drafting your story... (Stable Mode)")
    
    try:
        full_prompt = (f"Act as a professional author. Write a creative {user_data[chat_id]['length']} "
                       f"in {user_data[chat_id]['language']} about: '{message.text}'. "
                       "Output only the story text.")
        
        result = generate_groq_story(full_prompt)
        
        bot.delete_message(chat_id, msg.message_id)
        for chunk in split_message(result):
            bot.send_message(chat_id, chunk)
        user_data[chat_id] = {}
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ System Error: {str(e)}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
