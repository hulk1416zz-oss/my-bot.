import telebot
from telebot import types
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os
import threading
import http.server
import socketserver
import time

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

BOT_TOKEN = '8650413337:AAEzRMp-_NVTW3JtzSdK-G-6fv4NzNkExTk'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

user_links = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🔥 Hacker Mode Activated! Send YouTube Link.")

@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def ask(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 Summary", callback_data="pdf"),
               types.InlineKeyboardButton("🎵 Audio", callback_data="audio"))
    bot.reply_to(message, "What do you want to extract?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    
    c_file = 'cookies.txt' if os.path.exists('cookies.txt') and os.path.getsize('cookies.txt') > 0 else None

    if call.data == "pdf":
        bot.send_message(call.message.chat.id, "⏳ Bypassing restrictions for Summary...")
        try:
            v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            
            # التعديل البرمجي الصحيح لمكتبة النصوص
            if c_file:
                data = YouTubeTranscriptApi.get_transcript(v_id, cookies=c_file)
            else:
                data = YouTubeTranscriptApi.get_transcript(v_id)
                
            text = " ".join([i['text'] for i in data])
            res = model.generate_content(f"Summarize in Arabic as bullet points: {text[:20000]}")
            
            with open("sum.txt", "w", encoding="utf-8") as f: f.write(res.text)
            with open("sum.txt", "rb") as f: bot.send_document(call.message.chat.id, f, caption="✅ Summary extracted successfully!")
            os.remove("sum.txt")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ PDF Error details: {str(e)[:50]}") 

    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ Hacking YouTube Audio...")
        try:
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': 's.mp3',
                'cookiefile': c_file,
                'source_address': '0.0.0.0',
                'geo_bypass': True,
                'nocheckcertificate': True,
                'quiet': True,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
                'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            }
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            with open('s.mp3', 'rb') as f: bot.send_audio(call.message.chat.id, f, caption="✅ Audio extracted!")
            os.remove('s.mp3')
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Audio Error details: {str(e)[:50]}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
