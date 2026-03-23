import telebot
from telebot import types
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import os

# --- Settings ---
BOT_TOKEN = '8650413337:AAGsT4LjOfQUuOT_tP8-9tdio2dg71OuqTE'
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
    markup.add(types.InlineKeyboardButton("📄 Summary PDF", callback_data="pdf"),
               types.InlineKeyboardButton("🎵 Audio MP3", callback_data="audio"))
    bot.reply_to(message, "What do you need?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    url = user_links.get(call.message.chat.id)
    if not url: return

    if call.data == "pdf":
        bot.send_message(call.message.chat.id, "⏳ Generating Summary...")
        try:
            # استخراج الـ ID
            v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            
            # --- الحل الجذري للمشكلة ---
            # استخدام الطريقة الجديدة كلياً للمكتبة بعد التحديث
            api = YouTubeTranscriptApi()
            transcript_list = api.list(v_id)
            transcript = transcript_list.find_transcript(['en'])
            data = transcript.fetch()
            # --------------------------
            
            text = " ".join([i['text'] for i in data])
            
            res = model.generate_content(f"Summarize this in English with bullet points: {text[:25000]}")
            
            file_name = f"Summary_{v_id}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(res.text)
            
            with open(file_name, "rb") as f:
                bot.send_document(call.message.chat.id, f, caption="✅ Summary Done!")
            os.remove(file_name)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error extracting transcript. Details: {str(e)[:50]}")

    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ Extracting Audio...")
        try:
            opts = {'format': 'bestaudio/best', 'outtmpl': 'song.mp3', 'noplaylist': True}
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
            with open('song.mp3', 'rb') as f:
                bot.send_audio(call.message.chat.id, f)
            os.remove('song.mp3')
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Audio error. Details: {str(e)[:50]}")

bot.polling(none_stop=True)
