import telebot
from telebot import types
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os
import threading
import http.server
import socketserver

# --- سيرفر وهمي لإسكات Render ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    # استخدام 0.0.0.0 عشان السيرفر يمسك البورت صح
    with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

# --- التوكن الجديد ---
BOT_TOKEN = '8650413337:AAEzRMp-_NVTW3JtzSdK-G-6fv4NzNkExTk'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

user_links = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🌟 Bot is ready! Send me any YouTube link.")

@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def ask_options(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 Summary (TXT)", callback_data="pdf"),
               types.InlineKeyboardButton("🎵 Audio MP3", callback_data="audio"))
    bot.reply_to(message, "What do you need?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    url = user_links.get(call.message.chat.id)
    if not url: return

    if call.data == "pdf":
        bot.send_message(call.message.chat.id, "⏳ Generating Summary...")
        try:
            v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            transcript_list = YouTubeTranscriptApi.list_transcripts(v_id)
            transcript = next(iter(transcript_list)) 
            data = transcript.fetch()
            text = " ".join([i['text'] for i in data])
            
            res = model.generate_content(f"Summarize this in English with bullet points: {text[:25000]}")
            
            file_name = f"Summary_{v_id}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(res.text)
            with open(file_name, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption="✅ Summary Done!")
            os.remove(file_name)
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Error: Video must have subtitles/CC enabled.")

    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ Extracting Audio...")
        try:
            opts = {
                'format': 'bestaudio/best', 
                'outtmpl': 'song.mp3', 
                'noplaylist': True,
                'extractor_args': {'youtube': {'player_client': ['android', 'web']}} 
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            with open('song.mp3', 'rb') as f:
                bot.send_audio(call.message.chat.id, f)
            os.remove('song.mp3')
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Audio Error: YouTube blocked the download for this specific video. Try another one.")

bot.polling(none_stop=True)
