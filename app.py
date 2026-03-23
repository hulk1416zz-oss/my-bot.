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

# --- 1. الحفاظ على استقرار السيرفر ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
            httpd.serve_forever()
    except: pass

threading.Thread(target=keep_alive, daemon=True).start()

# --- 2. الإعدادات ---
BOT_TOKEN = '8650413337:AAEzRMp-_NVTW3JtzSdK-G-6fv4NzNkExTk'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 3. النواة الصلبة: تصنيع الكوكيز داخلياً بصيغة نقية ---
# هذا يلغي أي أخطاء مخفية تأتي من نسخ ولصق الجوال
def create_bulletproof_cookies():
    cookie_str = """# Netscape HTTP Cookie File
.youtube.com	FALSE	/	TRUE	0	VISITOR_PRIVACY_METADATA	CgJTQRIEGgAgHg%3D%3D
.youtube.com	FALSE	/	FALSE	0	ST-xuwub9	session_logininfo=AFmmF2swRQIhAPqRIUM2mGUYCL_lem7rnjjQNZ-3JF-M2S05AlZ7Z6SHAiBQ4o3-nh2tT47ks8qtEAc3BoqCcMtJEbuFPfZTLVkrgw%3AQUQ3MjNmekExVmdOTEZHX05ZNHNLYklqVnZ1Wk43NTZHLXNxeEpVLWVteUhub0dxMmw5SGU4cVMtMFZDNjN5S1lPUGNkV1BrdkhwTXpEblhWYzJ6cXdLRjFKN2xJNWtpRnR5MW9oWkktZW1lUC1jNkx1OWFQaENJWlMtaEE2WGNtM3JYWExLbEJPN2xLY3daaWxNMjJaSnY1eVR1cE91R1Nn
.youtube.com	FALSE	/	TRUE	0	__Secure-3PSID	g.a0008AgtDpEZjTiD0KAQj3qJ5wTyA8Gq_9H9w-KqdQ04Ixunj_IhbOjmcXg5ubxwPkNsgvDVAwACgYKASASARcSFQHGX2MiEymy6unXxwEgoh9vexiBjBoVAUF8yKr-KaDYuGHyew9OqPprzk4o0076
.youtube.com	FALSE	/	FALSE	0	SIDCC	AKEyXzXEyf1GLfx8ZRNkwjmS3MX3xISiXbIMBljmIQ7STLb1D25IDWwlv4vV5BxNRoFkh8-4rA
.youtube.com	FALSE	/	TRUE	1774346161	YSC	2mQ-ZqsgpYk
.youtube.com	FALSE	/	FALSE	0	SID	g.a0008AgtDpEZjTiD0KAQj3qJ5wTyA8Gq_9H9w-KqdQ04Ixunj_IhFU4fkbCKnoHTzayuDR8aYAACgYKAUsSARcSFQHGX2MigNG8u3M7jkZ0JDiJWJhSgxoVAUF8yKp30-nz9vjHrborvbJeJ6PA0076
.youtube.com	FALSE	/	TRUE	0	__Secure-1PSIDTS	sidts-CjUBWhotCfVVpyZBrNomg8l1kxER16F-4NPfCmZhlzDGZi55HTtLIJRf-ARsQfTJLUjj038elhAA
.youtube.com	FALSE	/	TRUE	0	SAPISID	XDJ-8m-uvNJgolWo/AQzVzzC0VxoOrGPhy
.youtube.com	FALSE	/	TRUE	0	__Secure-1PSIDCC	AKEyXzWKidJfFTHP1qKDJrYF06j9Un0311QsCGZ6btHZWzP3IU9pw7LhvjHkPQvRBNWrm987
.youtube.com	FALSE	/	TRUE	0	SSID	ASCXe6voYNalyZffS
.youtube.com	FALSE	/	TRUE	0	__Secure-1PAPISID	XDJ-8m-uvNJgolWo/AQzVzzC0VxoOrGPhy
.youtube.com	FALSE	/	TRUE	0	__Secure-1PSID	g.a0008AgtDpEZjTiD0KAQj3qJ5wTyA8Gq_9H9w-KqdQ04Ixunj_IhtFtRWUfcJiSyCytGkyG1UgACgYKAZwSARcSFQHGX2MiRtrIbSlFDDxI0Fw0KjoIEBoVAUF8yKrJC6aLnlv--Zt1JOFP3n4t0076
.youtube.com	FALSE	/	TRUE	0	__Secure-3PAPISID	XDJ-8m-uvNJgolWo/AQzVzzC0VxoOrGPhy
.youtube.com	FALSE	/	TRUE	0	__Secure-3PSIDCC	AKEyXzUtGuoNtqcRJCOl_Ke-43jE-eudPNwYbGEMTlz4I9YQmnkvlT24Oe0MN4vNSIR3_oIa
.youtube.com	FALSE	/	TRUE	0	__Secure-3PSIDTS	sidts-CjUBWhotCfVVpyZBrNomg8l1kxER16F-4NPfCmZhlzDGZi55HTtLIJRf-ARsQfTJLUjj038elhAA
.youtube.com	FALSE	/	TRUE	0	__Secure-ROLLOUT_TOKEN	CKKI-8S-ndHp9AEQqI7MwNe1kwMY7fn9wNe1kwM%3D
.youtube.com	FALSE	/	FALSE	0	APISID	_4Zrjrh1xqcG46s4/A5THCPCTY2JELCJa5
.youtube.com	FALSE	/	TRUE	0	CONSENT	YES+WIPR
.youtube.com	FALSE	/	FALSE	0	HSID	AdpSRfZxsHjYvjoEO
.youtube.com	FALSE	/	TRUE	0	LOGIN_INFO	AFmmF2swRQIhAPqRIUM2mGUYCL_lem7rnjjQNZ-3JF-M2S05AlZ7Z6SHAiBQ4o3-nh2tT47ks8qtEAc3BoqCcMtJEbuFPfZTLVkrgw:QUQ3MjNmekExVmdOTEZHX05ZNHNLYklqVnZ1Wk43NTZHLXNxeEpVLWVteUhub0dxMmw5SGU4cVMtMFZDNjN5S1lPUGNkV1BrdkhwTXpEblhWYzJ6cXdLRjFKN2xJNWtpRnR5MW9oWkktZW1lUC1jNkx1OWFQaENJWlMtaEE2WGNtM3JYWExLbEJPN2xLY3daaWxNMjJaSnY1eVR1cE91R1Nn
.youtube.com	FALSE	/	TRUE	0	PREF	f6=40000000&tz=Asia.Riyadh&f7=100&f4=4000000
.youtube.com	FALSE	/	TRUE	0	VISITOR_INFO1_LIVE	g6PzKmkd9es"""
    with open("server_cookies.txt", "w", encoding="utf-8", newline='\n') as f:
        f.write(cookie_str)
create_bulletproof_cookies()

user_links = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "✅ البوت جاهز تماماً للعمل (النسخة النهائية).")

@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def ask(message):
    user_links[message.chat.id] = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📄 التلخيص", callback_data="pdf"),
               types.InlineKeyboardButton("🎵 الصوت", callback_data="audio"))
    bot.reply_to(message, "ماذا تريد أن أستخرج من المقطع؟", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    url = user_links.get(call.message.chat.id)
    if not url: return

    if call.data == "pdf":
        bot.send_message(call.message.chat.id, "⏳ جاري استخراج النص وتلخيصه...")
        try:
            v_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1].split("?")[0]
            
            # 4. التعديل البرمجي المضمون الذي يعمل على جميع الإصدارات
            try:
                data = YouTubeTranscriptApi.get_transcript(v_id, languages=['ar', 'en', 'en-US'], cookies="server_cookies.txt")
            except:
                data = YouTubeTranscriptApi.get_transcript(v_id, languages=['ar', 'en', 'en-US'])
            
            text = " ".join([i['text'] for i in data])
            res = model.generate_content(f"لخص هذا النص على شكل نقاط مفيدة باللغة العربية: {text[:20000]}")
            
            with open("Summary.txt", "w", encoding="utf-8") as f: f.write(res.text)
            with open("Summary.txt", "rb") as f: bot.send_document(call.message.chat.id, f, caption="✅ تم استخراج الملخص بنجاح.")
            os.remove("Summary.txt")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ تعذر الاستخراج. السبب التقني: {str(e)[:50]}")

    elif call.data == "audio":
        bot.send_message(call.message.chat.id, "⏳ جاري تحميل الصوت بأقصى جودة...")
        try:
            # 5. محاولة التحميل كجهاز أندرويد وآيفون
            opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.mp3',
                'cookiefile': 'server_cookies.txt',
                'nocheckcertificate': True,
                'quiet': True,
                'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}
            }
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            with open('audio.mp3', 'rb') as f: bot.send_audio(call.message.chat.id, f, caption="✅ تم استخراج الصوت بنجاح.")
            os.remove('audio.mp3')
        except Exception as e:
            # 6. خطة الطوارئ: محاولة التحميل كشاشة تلفزيون إذا تم حظر الجوال
            bot.send_message(call.message.chat.id, "⚠️ يوتيوب يقاوم... جاري تجربة مسار بديل...")
            try:
                opts_no_cookie = {
                    'format': 'm4a/bestaudio/best',
                    'outtmpl': 'audio2.mp3',
                    'nocheckcertificate': True,
                    'quiet': True,
                    'extractor_args': {'youtube': {'player_client': ['tv', 'web']}}
                }
                with yt_dlp.YoutubeDL(opts_no_cookie) as ydl: ydl.download([url])
                with open('audio2.mp3', 'rb') as f: bot.send_audio(call.message.chat.id, f)
                os.remove('audio2.mp3')
            except Exception as e2:
                bot.send_message(call.message.chat.id, f"❌ فشل التحميل. السبب التقني: {str(e2)[:50]}")

while True:
    try: bot.polling(none_stop=True)
    except: time.sleep(3)
