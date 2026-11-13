import os
from gtts import gTTS
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

# قاموس لحفظ اللغة واللهجة الخاصة بكل مستخدم (الافتراضي: العربية)
user_settings = {}


def get_settings(chat_id):
  if chat_id not in user_settings:
    user_settings[chat_id] = {'lang': 'ar', 'tld': 'com'}
  return user_settings[chat_id]


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  # إنشاء لوحة أزرار تحتوي على 12 صوت/لغة مختلفة
  markup = InlineKeyboardMarkup(row_width=2)
  markup.add(
      InlineKeyboardButton('🇸🇦 العربية', callback_data='lang_ar'),
      InlineKeyboardButton('🇺🇸 إنجليزي (أمريكي)', callback_data='lang_en_us'),
      InlineKeyboardButton('🇬🇧 إنجليزي (بريطاني)', callback_data='lang_en_uk'),
      InlineKeyboardButton('🇫🇷 الفرنسية', callback_data='lang_fr'),
      InlineKeyboardButton('🇪🇸 الإسبانية', callback_data='lang_es'),
      InlineKeyboardButton('🇩🇪 الألمانية', callback_data='lang_de'),
      InlineKeyboardButton('🇮🇹 الإيطالية', callback_data='lang_it'),
      InlineKeyboardButton('🇹🇷 التركية', callback_data='lang_tr'),
      InlineKeyboardButton('🇷🇺 الروسية', callback_data='lang_ru'),
      InlineKeyboardButton('🇯🇵 اليابانية', callback_data='lang_ja'),
      InlineKeyboardButton('🇰🇷 الكورية', callback_data='lang_ko'),
      InlineKeyboardButton('🇧🇷 البرتغالية', callback_data='lang_pt'),
  )

  welcome_text = (
      'مرحباً بك يا إسماعيل في بوت تحويل النص إلى صوت! 🎙️\n\n• اختر الصوت أو'
      ' اللّغة المفضلة لديك من الأزرار أدناه، ثم أرسل لي أي نص لتحويله مباشرة'
      ' إلى رسالة صوتية.'
  )
  bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# استقبال الضغط على الأزرار وتغيير لغة المستخدم
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
  chat_id = call.message.chat.id
  data = call.data
  settings = get_settings(chat_id)

  lang_name = ''
  if data == 'lang_ar':
    settings['lang'], settings['tld'], lang_name = 'ar', 'com', 'العربية 🇸🇦'
  elif data == 'lang_en_us':
    settings['lang'], settings['tld'], lang_name = (
        'en',
        'com',
        'الإنجليزية (أمريكي) 🇺🇸',
    )
  elif data == 'lang_en_uk':
    settings['lang'], settings['tld'], lang_name = (
        'en',
        'co.uk',
        'الإنجليزية (بريطاني) 🇬🇧',
    )
  elif data == 'lang_fr':
    settings['lang'], settings['tld'], lang_name = 'fr', 'com', 'الفرنسية 🇫🇷'
  elif data == 'lang_es':
    settings['lang'], settings['tld'], lang_name = 'es', 'com', 'الإسبانية 🇪🇸'
  elif data == 'lang_de':
    settings['lang'], settings['tld'], lang_name = 'de', 'com', 'الألمانية 🇩🇪'
  elif data == 'lang_it':
    settings['lang'], settings['tld'], lang_name = 'it', 'com', 'الإيطالية 🇮🇹'
  elif data == 'lang_tr':
    settings['lang'], settings['tld'], lang_name = 'tr', 'com', 'التركية 🇹🇷'
  elif data == 'lang_ru':
    settings['lang'], settings['tld'], lang_name = 'روسية', 'com', 'الروسية 🇷🇺'
  elif data == 'lang_ja':
    settings['lang'], settings['tld'], lang_name = 'ja', 'com', 'اليابانية 🇯🇵'
  elif data == 'lang_ko':
    settings['lang'], settings['tld'], lang_name = 'ko', 'com', 'الكورية 🇰🇷'
  elif data == 'lang_pt':
    settings['lang'], settings['tld'], lang_name = (
        'pt',
        'com',
        'البرتغالية 🇧🇷',
    )

  bot.answer_callback_query(
      call.id, text=f'تم تفعيل الصوت: {lang_name}', show_alert=False
  )
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          f'✅ تم اختيار **{lang_name}** بنجاح!\n\nالآن أرسل لي أي نص وسأقوم'
          ' بتحويله فوراً إلى صوت.'
      ),
      parse_mode='Markdown',
  )


@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  chat_id = message.chat.id
  text_to_convert = message.text
  settings = get_settings(chat_id)

  processing_msg = bot.reply_to(message, '🎙️ جاري تحويل النص إلى صوت...')

  try:
    # توليد الملف الصوتي بناءً على إعدادات اللغة المختارة للمستخدم
    tts = gTTS(
        text=text_to_convert,
        lang=settings['lang'],
        tld=settings['tld'],
        slow=False,
    )
    audio_path = 'output_audio.mp3'
    tts.save(audio_path)

    # إرسال الملف الصوتي كرسالة صوتية (Voice)
    with open(audio_path, 'rb') as audio:
      bot.send_voice(chat_id, audio)

    # حذف رسالة الانتظار وملف الصوت المؤقت
    bot.delete_message(chat_id, processing_msg.message_id)
    if os.path.exists(audio_path):
      os.remove(audio_path)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ أثناء تحويل النص: {e}')


if __name__ == '__main__':
  print('Bot is running with voice selection...')
  bot.remove_webhook()
  bot.infinity_polling()
