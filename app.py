import telebot
from telebot import types
import google.generativeai as genai
import os
import threading
import http.server
import socketserver
import time

# --- خادم الويب (عشان السيرفر ما ينام) ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- مفاتيحك الخاصة (تم دمجها بنجاح) ---
BOT_TOKEN = '8675888280:AAHS50UdimC3vlFvBDPQKBotBBZN8q2U-h4' 
GEMINI_API_KEY = 'AIzaSyDV9ta8FFiIBKIqNMIcCVlCp_-h8GJhXtc' 

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# استخدام أسرع وأحدث نموذج ذكاء اصطناعي
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
    bot.reply_to(message, "Welcome to the AI Author Bot! 📚\n\nPlease select the language for your story:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def choose_length(call):
    lang = call.data.split('_')[1]
    user_data[call.message.chat.id]['language'] = lang
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Short Story (~3 Pages)", callback_data="len_Short Story"),
               types.InlineKeyboardButton("Detailed Chapter (~6 Pages)", callback_data="len_Detailed Chapter"))
    
    bot.edit_message_text(f"Language set to: **{lang}** ✅\n\nNow, select the length of your text:",
                          chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('len_'))
def ask_prompt(call):
    length = call.data.split('_')[1]
    user_data[call.message.chat.id]['length'] = length
    
    bot.edit_message_text(f"Length set to: **{length}** ✅\n\nGreat! Now send me the title, idea, or plot of your story:",
                          chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda message: True)
def generate_story(message):
    chat_id = message.chat.id
    
    if chat_id not in user_data or 'language' not in user_data[chat_id] or 'length' not in user_data[chat_id]:
        bot.reply_to(message, "Please use /start to configure your story settings first.")
        return

    msg = bot.reply_to(message, "⏳ The AI is currently writing your masterpiece. This might take a minute...")
    
    lang = user_data[chat_id]['language']
    length = user_data[chat_id]['length']
    user_idea = message.text
    
    try:
        prompt = f"""
        Act as a New York Times bestselling author. Write a highly engaging and creative {length} based strictly on this idea/title: '{user_idea}'.
        The story MUST be written in {lang}.
        Make the tone suitable for a mature Western audience. Include rich environmental descriptions, compelling character hooks, and natural dialogue.
        Output ONLY the story text. Do not include any introductory or concluding remarks or markdown formatting like bolding unless necessary.
        """
        
        response = model.generate_content(prompt)
        story = response.text
        
        bot.delete_message(chat_id, msg.message_id) 
        
        for chunk in split_message(story):
            bot.send_message(chat_id, chunk)
            
        user_data[chat_id] = {}
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ Google API Error: {str(e)[:150]}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
