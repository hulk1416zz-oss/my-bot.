import telebot
from telebot import types
import requests
import os
import threading
import http.server
import socketserver
import time

# --- خادم الويب (Keep Alive) ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- الإعدادات النهائية ---
BOT_TOKEN = '8675888280:AAHS50UdimC3vlFvBDPQKBotBBZN8q2U-h4'
GROQ_API_KEY = 'Gsk_csE1OleO06dttE0o05J2WGdyb3FYQzHo5cv0dlRmUIBwEYtNvH57'

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def split_message(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# دالة التواصل مع ذكاء Groq الخارق
def generate_groq_story(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile", # أقوى موديل عندهم حالياً
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

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
    bot.edit_message_text("Select the length:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('len_'))
def ask_prompt(call):
    user_data[call.message.chat.id]['length'] = call.data.split('_')[1]
    bot.edit_message_text("Great! Now send me your story title or idea:", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_story(message):
    chat_id = message.chat.id
    if chat_id not in user_data or 'language' not in user_data[chat_id]:
        bot.reply_to(message, "Please use /start to configure your story.")
        return

    msg = bot.reply_to(message, "⏳ AI is drafting your masterpiece... (Ultra Fast Mode)")
    
    try:
        full_prompt = (f"Act as a professional best-selling author. Write a creative {user_data[chat_id]['length']} "
                       f"in {user_data[chat_id]['language']} about: '{message.text}'. "
                       "Make it high quality for a Western audience. Output only the story.")
        
        story = generate_groq_story(full_prompt)
        
        bot.delete_message(chat_id, msg.message_id)
        for chunk in split_message(story):
            bot.send_message(chat_id, chunk)
            
        user_data[chat_id] = {}
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)[:100]}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
