import os
from gtts import gTTS
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

# قاموس لحفظ خيارات اللهجة الخاصة بكل مستخدم
user_settings = {}


def get_settings(chat_id):
  if chat_id not in user_settings:
    user_settings[chat_id] = {'lang': 'en', 'tld': 'com', 'slow': False}
  return user_settings[chat_id]


# الخطوة 1: عرض أزرار اللهجات الحقيقية المختلفة
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  markup = InlineKeyboardMarkup(row_width=2)
  markup.add(
      InlineKeyboardButton('🇺🇸 إنجليزي (أمريكي سريح)', callback_data='voice_en_us'),
      InlineKeyboardButton('🇬🇧 إنجليزي (بريطاني رصين)', callback_data='voice_en_uk'),
      InlineKeyboardButton('🇦🇺 إنجليزي (أسترالي)', callback_data='voice_en_au'),
      InlineKeyboardButton('🇮🇳 إنجليزي (هندي)', callback_data='voice_en_in'),
      InlineKeyboardButton('🇨🇦 إنجليزي (كندي)', callback_data='voice_en_ca'),
      InlineKeyboardButton('🇫🇷 فرنسية (رسمية)', callback_data='voice_fr'),
      InlineKeyboardButton('🇪🇸 إسبانية', callback_data='voice_es'),
      InlineKeyboardButton('🇩🇪 ألمانية', callback_data='voice_de'),
      InlineKeyboardButton(
          '🐢 إنجليزي بطيء (للتدريب والتعلم)', callback_data='voice_en_slow'
      ),
      InlineKeyboardButton('🎧 العربية الافتراضية', callback_data='voice_ar'),
  )

  welcome_text = (
      'مرحباً بك يا إسماعيل! 🎙️\n\nاختر **اللهجة أو النبرة الحقيقية** التي'
      ' تريدها من الأزرار أدناه، وسيتغير الصوت فعلياً:'
  )
  bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# الخطوة 2: استقبال الضغط وتغيير إعدادات الصوت البرمجية الحقيقية
@bot.callback_query_handler(func=lambda call: call.data.startswith('voice_'))
def set_voice_style(call):
  chat_id = call.message.chat.id
  data = call.data
  settings = get_settings(chat_id)

  voice_name = ''

  if data == 'voice_en_us':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'com', False
    voice_name = '🇺🇸 إنجليزي أمريكي'
  elif data == 'voice_en_uk':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'co.uk', False
    voice_name = '🇬🇧 إنجليزي بريطاني'
  elif data == 'voice_en_au':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'com.au', False
    voice_name = '🇦🇺 إنجليزي أسترالي'
  elif data == 'voice_en_in':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'co.in', False
    voice_name = '🇮🇳 إنجليزي هندي'
  elif data == 'voice_en_ca':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'ca', False
    voice_name = '🇨🇦 إنجليزي كندي'
  elif data == 'voice_fr':
    settings['lang'], settings['tld'], settings['slow'] = 'fr', 'com', False
    voice_name = '🇫🇷 فرنسية'
  elif data == 'voice_es':
    settings['lang'], settings['tld'], settings['slow'] = 'es', 'com', False
    voice_name = '🇪🇸 إسبانية'
  elif data == 'voice_de':
    settings['lang'], settings['tld'], settings['slow'] = 'de', 'com', False
    voice_name = '🇩🇪 ألمانية'
  elif data == 'voice_en_slow':
    settings['lang'], settings['tld'], settings['slow'] = 'en', 'com', True
    voice_name = '🐢 إنجليزي بطيء جداً'
  elif data == 'voice_ar':
    settings['lang'], settings['tld'], settings['slow'] = 'ar', 'com', False
    voice_name = '🎧 العربية'

  bot.answer_callback_query(call.id, text=f'تم تغيير الصوت إلى: {voice_name}')
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          f'✅ تم اختيار صوتیات: **{voice_name}** بنجاح!\n\nالآن أرسل لي النص'
          ' لتسمع الفارق الحقيقي في النبرة واللهجة.'
      ),
      parse_mode='Markdown',
  )


# الخطوة 3: توليد الصوت الفعلي وإرساله
@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  chat_id = message.chat.id
  text_to_convert = message.text
  settings = get_settings(chat_id)

  processing_msg = bot.reply_to(message, '🎙️ جاري توليد الصوت باللهجة المختارة...')

  try:
    # استخدام الإعدادات الحقيقية لتغيير النبرة واللهجة والسرعة
    tts = gTTS(
        text=text_to_convert,
        lang=settings['lang'],
        tld=settings['tld'],
        slow=settings['slow'],
    )
    audio_path = 'output_audio.mp3'
    tts.save(audio_path)

    with open(audio_path, 'rb') as audio:
      bot.send_voice(chat_id, audio)

    bot.delete_message(chat_id, processing_msg.message_id)
    if os.path.exists(audio_path):
      os.remove(audio_path)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ: {e}')


if __name__ == '__main__':
  print('Bot with real accent switching is running...')
  bot.remove_webhook()
  bot.infinity_polling()
