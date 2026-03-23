import telebot
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import os
import re

# --- الإعدادات ---
BOT_TOKEN = '8650413337:AAGsT4LjOfQUuOT_tP8-9tdio2dg71OuqTE'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# دالة لاستخراج ID الفيديو من الرابط
def get_video_id(url):
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🎯 أهلاً بك! أرسل لي رابط فيديو يوتيوب وسأقوم بتحويله إلى ملخص PDF احترافي فوراً.")

@bot.message_handler(func=lambda message: 'youtube.com' in message.text or 'youtu.be' in message.text)
def handle_youtube(message):
    video_id = get_video_id(message.text)
    if not video_id:
        bot.reply_to(message, "❌ عذراً، الرابط غير صحيح.")
        return

    msg = bot.reply_to(message, "⏳ جاري استخراج النص وتلخيصه... انتظر قليلاً.")
    
    try:
        # 1. سحب النص من اليوتيوب
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar', 'en'])
        full_text = " ".join([t['text'] for t in transcript_list])

        # 2. تلخيص النص باستخدام Gemini
        prompt = f"قم بتلخيص هذا النص بشكل احترافي ومنظم على شكل نقاط رئيسية وشرح مفصل باللغة العربية: {full_text[:30000]}"
        response = model.generate_content(prompt)
        summary = response.text

        # 3. إنشاء ملف PDF
        pdf = FPDF()
        pdf.add_page()
        # ملاحظة: المكتبة العادية لا تدعم العربي جيداً بدون خطوط، لذا سنكتب النص بشكل مبدئي
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt="YouTube Video Summary\n\n" + summary.encode('latin-1', 'ignore').decode('latin-1'))
        
        pdf_file = f"{video_id}.pdf"
        pdf.output(pdf_file)

        # 4. إرسال الملف للمستخدم
        with open(pdf_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="✅ تم تجهيز ملخص الفيديو بنجاح!")
        
        os.remove(pdf_file) # حذف الملف بعد الإرسال
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: تأكد أن الفيديو يحتوي على ترجمة (Subtitles).\nالتفاصيل: {str(e)[:100]}")

bot.polling()
