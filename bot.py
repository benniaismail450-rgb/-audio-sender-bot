import os
from gtts import gTTS
import telebot

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  welcome_text = (
      'مرحباً بك يا إسماعيل في بوت تحويل النص إلى صوت! 🎙️\n\n• أرسل لي أي نص'
      ' وسأقوم بتحويله فوراً إلى رسالة صوتية مسموعة.'
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
  print('Bot is running successfully...')
  bot.remove_webhook()
  bot.infinity_polling()
