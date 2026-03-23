import telebot
import google.generativeai as genai
import os

# --- الإعدادات (التوكنات) ---
# ملاحظة: يفضل مستقبلاً وضعها في Environment Variables للأمان
BOT_TOKEN = '8650413337:AAGsT4LjOfQUuOT_tP8-9tdio2dg71OuqTE'
GEMINI_API_KEY = 'AIzaSyB_Q2nleMzyVncqfwgnrTSEnaO4r4jr0JY'

# تشغيل البوت والذكاء الاصطناعي
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- الأوامر ---

# رد عند كتابة /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🚀 أهلاً بك في بوت الذكاء الاصطناعي!\n"
        "أنا شغال الآن على سيرفر Render المستقر.\n"
        "أرسل لي أي سؤال وسأجيبك فوراً باستخدام Gemini."
    )
    bot.reply_to(message, welcome_text)

# الرد على الرسائل النصية
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    try:
        # إرسال النص لـ Gemini للحصول على رد
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "عذراً، حدث خطأ بسيط في معالجة طلبك. جرب مرة أخرى.")
        print(f"Error: {e}")

# تشغيل البوت باستمرار
if __name__ == "__main__":
    print("البوت بدأ العمل بنجاح...")
    bot.polling(none_stop=True)
