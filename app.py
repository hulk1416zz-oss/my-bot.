import telebot
from telebot import types
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os

# --- التوكن والـ API ---
BOT_TOKEN = '8650413337:AAEzRMp-_NVTW3JtzSdK-G-6fv4NzNkExTk'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

user_links = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🌟 Ready with Cookies! Send link.")

@bot.message_handler(func=lambda m: 'youtube' in m.text or 'youtu.be' in m.text)
def ask(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 Summary", callback_data="pdf"),
               types.InlineKeyboardButton("🎵 Audio", callback_data="audio"))
    bot.reply_to(message, "Choice:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    c_file = 'cookies.txt' if os.path.exists('cookies.txt') else None

    if call.data == "pdf":
        bot.send_message(call.message.chat.id, "⏳ Summarizing...")
        try:
            v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            # استخدام الكوكيز لسحب النص
            t_list = YouTubeTranscriptApi.list_transcripts(v_id, cookies=c_file) if c_file else YouTubeTranscriptApi.list_transcripts(v_id)
            data = next(iter(t_list)).fetch()
            text = " ".join([i['text'] for i in data])
            res = model.generate_content(f"Summarize in English: {text[:25000]}")
            with open("sum.txt", "w", encoding="utf-8") as f: f.write(res.text)
            with open("sum.txt", "rb") as f: bot.send_document(call.message.chat.id, f)
        except Exception as e: bot.send_message(call.message.chat.id, "❌ PDF Error.")

    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ Downloading Audio...")
        try:
            opts = {'format': 'bestaudio', 'outtmpl': 's.mp3', 'cookiefile': c_file} if c_file else {'format': 'bestaudio', 'outtmpl': 's.mp3'}
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            with open('s.mp3', 'rb') as f: bot.send_audio(call.message.chat.id, f)
            os.remove('s.mp3')
        except Exception as e: bot.send_message(call.message.chat.id, "❌ Audio Error.")

bot.polling(none_stop=True)
