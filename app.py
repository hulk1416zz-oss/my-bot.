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

user_data = {} # لحفظ الرابط مؤقتاً لكل مستخدم

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Send me a YouTube link to start.")

@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def handle_link(message):
    url = message.text
    user_data[message.chat.id] = url
    
    # إنشاء الأزرار
    markup = types.InlineKeyboardMarkup()
    btn_pdf = types.InlineKeyboardButton("📄 Summary PDF", callback_data="gen_pdf")
    btn_audio = types.InlineKeyboardButton("🎵 Download Audio (MP3)", callback_data="gen_audio")
    markup.add(btn_pdf, btn_audio)
    
    bot.reply_to(message, "What would you like to do with this video?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_data.get(call.message.chat.id)
    if not url:
        bot.answer_callback_query(call.id, "❌ Error: Link not found. Send the link again.")
        return

    if call.data == "gen_pdf":
        bot.answer_callback_query(call.id, "⏳ Generating PDF...")
        process_pdf(call.message, url)
        
    elif call.data == "gen_audio":
        bot.answer_callback_query(call.id, "⏳ Extracting Audio...")
        process_audio(call.message, url)

# --- وظيفة تحويل الـ PDF ---
def process_pdf(message, url):
    try:
        video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        full_text = " ".join([t['text'] for t in transcript])
        
        response = model.generate_content(f"Summarize this in English: {full_text[:30000]}")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, response.text)
        
        file_name = f"Summary_{video_id}.pdf"
        pdf.output(file_name)
        
        with open(file_name, 'rb') as f:
            bot.send_document(message.chat.id, f)
        os.remove(file_name)
    except:
        bot.send_message(message.chat.id, "❌ Could not generate PDF. Check subtitles.")

# --- وظيفة تحويل الصوت ---
def process_audio(message, url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'audio_file.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open('audio_file.mp3', 'rb') as f:
            bot.send_audio(message.chat.id, f, caption="✅ Your Audio is ready!")
        os.remove('audio_file.mp3')
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Audio Error: {str(e)[:50]}")

bot.polling()
