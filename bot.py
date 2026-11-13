import os
from gtts import gTTS
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

# قاموس لحفظ اختيارات المستخدم (اللغة + النبرة/الأسلوب)
user_settings = {}


def get_settings(chat_id):
  if chat_id not in user_settings:
    user_settings[chat_id] = {'lang': 'ar', 'style': 'normal', 'tld': 'com'}
  return user_settings[chat_id]


# الخطوة 1: أمر البدء لعرض اللغات الأساسية
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  markup = InlineKeyboardMarkup(row_width=2)
  markup.add(
      InlineKeyboardButton('🇸🇦 العربية', callback_data='lang_ar'),
      InlineKeyboardButton('🇺🇸 الإنجليزية', callback_data='lang_en'),
      InlineKeyboardButton('🇫🇷 الفرنسية', callback_data='lang_fr'),
      InlineKeyboardButton('🇪🇸 الإسبانية', callback_data='lang_es'),
      InlineKeyboardButton('🇩🇪 الألمانية', callback_data='lang_de'),
      InlineKeyboardButton('🇹🇷 التركية', callback_data='lang_tr'),
  )

  welcome_text = (
      'مرحباً بك يا إسماعيل في بوت تحويل النص إلى صوت المطور! 🎙️\n\n• الخطوة'
      ' الأولى: اختر **اللغة** الأساسية من الأزرار أدناه:'
  )
  bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# الخطوة 2: استقبال اختيار اللغة والانتقال لاختيار النبرة/اللهجة الإبداعية
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_language(call):
  chat_id = call.message.chat.id
  lang_code = call.data.split('_')[1]
  settings = get_settings(chat_id)
  settings['lang'] = lang_code

  # إنشاء لوحة أزرار اللهجات والنبرات المميزة
  markup = InlineKeyboardMarkup(row_width=1)
  markup.add(
      InlineKeyboardButton(
          '🌍 نبرة وثائقية (ناشيونال جيوغرافيك)', callback_data='style_natgeo'
      ),
      InlineKeyboardButton(
          '🎖️ نبرة عسكرية (جنرال حرب)', callback_data='style_general'
      ),
      InlineKeyboardButton('👶 نبرة أطفال', callback_data='style_kid'),
      InlineKeyboardButton(
          '🎬 نبرة سينمائية تشويقية', callback_data='style_cinema'
      ),
      InlineKeyboardButton('🤖 نبرة روبوت آلية', callback_data='style_robot'),
      InlineKeyboardButton('⚡ نبرة حماسية سريعة', callback_data='style_fast'),
      InlineKeyboardButton(
          '🎧 النبرة العادية (الافتراضية)', callback_data='style_normal'
      ),
  )

  bot.answer_callback_query(call.id, text='تم حفظ اللغة، اختر النبرة الآن')
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          '✅ ممتاز! الخطوة الثانية:\nاختر **الطابع أو النبرة الإبداعية**'
          ' التي تريد أن يقرأ بها الصوت:'
      ),
      reply_markup=markup,
  )


# الخطوة 3: استقبال اختيار النبرة وتجهيز النص
@bot.callback_query_handler(func=lambda call: call.data.startswith('style_'))
def set_style(call):
  chat_id = call.message.chat.id
  style_code = call.data.split('_')[1]
  settings = get_settings(chat_id)
  settings['style'] = style_code

  style_names = {
      'natgeo': '🌍 وثائقية (ناشيونال جيوغرافيك)',
      'general': '🎖️ عسكرية (جنرال حرب)',
      'kid': '👶 أطفال',
      'cinema': '🎬 سينمائية تشويقية',
      'robot': '🤖 روبوت آلية',
      'fast': '⚡ حماسية سريعة',
      'normal': '🎧 عادية',
  }

  chosen_style_name = style_names.get(style_code, 'عادية')

  bot.answer_callback_query(
      call.id, text=f'تم تفعيل النبرة: {chosen_style_name}'
  )
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          f'🎉 تم ضبط الإعدادات بنجاح!\n\n• اللغة: `{settings["lang"]}`\n•'
          f' النبرة: **{chosen_style_name}**\n\nالآن أرسل لي أي نص وسأقوم'
          ' بتعديله وإرساله بصوت مطابق لهذه النبرة!'
      ),
  )


# معالجة النص وتعديله وفقاً للنبرة المختارة قبل تحويله لصوت
@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  chat_id = message.chat.id
  original_text = message.text
  settings = get_settings(chat_id)

  style = settings.get('style', 'normal')
  processed_text = original_text

  # تعديل صياغة النص برمجيياً ليعطي إيحاء النبرة عند القراءة الصوتية
  if style == 'natgeo':
    processed_text = (
        'في عوالم الطبيعة الساحرة، وحيث تتكشف أسرار البرية... '
        + original_text
        + ' .. هكذا تستمر الحياة في كوكبنا.'
    )
    settings['tld'] = 'com'
    slow_speed = True  # بطء متعمد لإعطاء طابع وثائقي هادئ

  elif style == 'general':
    processed_text = (
        'تنبيه عسكري هام. انصتوا جيداً للتعليمات الآتية: '
        + original_text
        + ' .. انتهى البيان.'
    )
    settings['tld'] = 'com'
    slow_speed = False

  elif style == 'kid':
    processed_text = (
        'مرحباً أصدقائي الصغار! اسمعوا هذه الحكاية الجميلة: '
        + original_text
        + ' .. يا لها من متعة!'
    )
    settings['tld'] = 'com'
    slow_speed = False

  elif style == 'cinema':
    processed_text = (
        'في عالم مليء بالغموض والأحداث المرتقبة... '
        + original_text
        + ' .. انتظرونا في الجزء القادم.'
    )
    settings['tld'] = 'com'
    slow_speed = False

  elif style == 'robot':
    # إضافة تقطيع شبيه بالروبوتات
    processed_text = '. '.join(list(original_text))
    settings['tld'] = 'com'
    slow_speed = False

  elif style == 'fast':
    processed_text = original_text + ' بسرعة البرق وبدون توقف.'
    settings['tld'] = 'com'
    slow_speed = False

  else:  # العادية
    processed_text = original_text
    settings['tld'] = 'com'
    slow_speed = False

  processing_msg = bot.reply_to(
      message, '🎙️ جاري هندسة الصوت وتطبيق النبرة المختارة...'
  )

  try:
    # توليد ملف الصوت بناءً على الإعدادات
    tts = gTTS(
        text=processed_text,
        lang=settings['lang'],
        tld=settings['tld'],
        slow=slow_speed,
    )
    audio_path = 'output_audio.mp3'
    tts.save(audio_path)

    # إرسال الملف الصوتي كرسالة صوتية (Voice)
    with open(audio_path, 'rb') as audio:
      bot.send_voice(chat_id, audio)

    # تنظيف الرسائل والملفات المؤقتة
    bot.delete_message(chat_id, processing_msg.message_id)
    if os.path.exists(audio_path):
      os.remove(audio_path)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ أثناء معالجة الصوت: {e}')


if __name__ == '__main__':
  print('Bot with styles & accents is running...')
  bot.remove_webhook()
  bot.infinity_polling()
