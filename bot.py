import os
from flask import Flask, request
from gtts import gTTS
import telebot

# التوكن الجديد الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/')
def home():
  return 'TTS Telegram Bot is active and running successfully!'


@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
  if request.headers.get('content-type') == 'application/json':
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200
  else:
    return 'Forbidden', 403


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  welcome_text = (
      'مرحباً بك في بوت تحويل النص إلى صوت! 🎙️\n\n• أرسل لي أي نص (بالعربية أو'
      ' الإنجليزية) وسأقوم بتحويله فوراً إلى رسالة صوتية مسموعة.'
  )
  bot.reply_to(message, welcome_text)


@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  text_to_convert = message.text
  processing_msg = bot.reply_to(message, '🎙️ جاري تحويل النص إلى صوت...')

  try:
    # توليد الملف الصوتي باستخدام gTTS
    tts = gTTS(text=text_to_convert, lang='ar', slow=False)
    audio_path = 'output_audio.mp3'
    tts.save(audio_path)

    # إرسال الملف الصوتي كرسالة صوتية (Voice) للمستخدم
    with open(audio_path, 'rb') as audio:
      bot.send_voice(message.chat.id, audio)

    # حذف رسالة الانتظار وملف الصوت المؤقت
    bot.delete_message(message.chat.id, processing_msg.message_id)
    if os.path.exists(audio_path):
      os.remove(audio_path)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ أثناء تحويل النص: {e}')


if __name__ == '__main__':
  bot.remove_webhook()
  RENDER_URL = f'https://ai-sms-ocr-bot.onrender.com/{TOKEN}'
  bot.set_webhook(url=RENDER_URL)

  port = int(os.environ.get('PORT', 10000))
  app.run(host='0.0.0.0', port=port)
