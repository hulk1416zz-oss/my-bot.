import telebot
from telebot import types
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import yt_dlp
import os

# --- Setup ---
BOT_TOKEN = '8650413337:AAGsT4LjOfQUuOT_tP8-9tdio2dg71OuqTE'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🌟 Welcome! Send me a YouTube link to get a PDF summary or Audio.")

@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def handle_link(message):
    url = message.text
    user_data[message.chat.id] = url
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 Summary PDF", callback_data="gen_pdf"),
               types.InlineKeyboardButton("🎵 Audio MP3", callback_data="gen_audio"))
    bot.reply_to(message, "Choose an option:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_data.get(call.message.chat.id)
    if not url: return

    if call.data == "gen_pdf":
        bot.send_message(call.message.chat.id, "⏳ Processing PDF Summary...")
        try:
            # تصحيح الـ ID وسحب النص
            video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            # هنا التعديل الصحيح لاستدعاء المكتبة
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            full_text = " ".join([t['text'] for t in transcript])
            
            response = model.generate_content(f"Summarize in English with bullet points: {full_text[:30000]}")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, response.text.encode('latin-1', 'ignore').decode('latin-1'))
            
            file_name = f"Summary_{video_id}.pdf"
            pdf.output(file_name)
            with open(file_name, 'rb') as f:
                bot.send_document(call.message.chat.id, f)
            os.remove(file_name)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error: {str(e)[:100]}")

    elif call.data == "gen_audio":
        bot.send_message(call.message.chat.id, "⏳ Extracting Audio... (May take a minute)")
        try:
            ydl_opts = {'format': 'bestaudio/best', 'outtmpl': 'audio.mp3'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('audio.mp3', 'rb') as f:
                bot.send_audio(call.message.chat.id, f)
            os.remove('audio.mp3')
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Audio error. Try a shorter video.")

bot.polling(none_stop=True)
