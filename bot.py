import os
from gtts import gTTS
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

# قاموس حفظ إعدادات النبرة لكل مستخدم
user_settings = {}


def get_settings(chat_id):
  if chat_id not in user_settings:
    user_settings[chat_id] = {
        'style': 'normal',
        'lang': 'ar',
        'tld': 'com',
        'slow': False,
    }
  return user_settings[chat_id]


# واجهة اختيار النبرات واللهجات الإبداعية بشكل راقي ونظيف
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  markup = InlineKeyboardMarkup(row_width=1)
  markup.add(
      InlineKeyboardButton(
          '🌍 نبرة ناشيونال جيوغرافيك (وثائقي هادئ)', callback_data='style_natgeo'
      ),
      InlineKeyboardButton(
          '🎖️ نبرة عسكرية (حازم ورسمي)', callback_data='style_military'
      ),
      InlineKeyboardButton(
          '🤖 نبرة روبوت آلية (تقنية)', callback_data='style_robot'
      ),
      InlineKeyboardButton(
          '🐢 نبرة بطيئة جداً (للتدقيق والتعلم)', callback_data='style_slow'
      ),
      InlineKeyboardButton(
          '🎧 النبرة العربية العادية', callback_data='style_normal'
      ),
  )

  welcome_text = (
      'مرحباً بك في خدمة التحويل الصوتي الاحترافية. 🎙️\n\nيرجى اختيار النبرة'
      ' أو الطابع الصوتي المطلوب من القائمة أدناه:'
  )
  bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# استقبال اختيار النبرة وتحديث إعدادات المستخدم
@bot.callback_query_handler(func=lambda call: call.data.startswith('style_'))
def set_voice_style(call):
  chat_id = call.message.chat.id
  data = call.data
  settings = get_settings(chat_id)
  style_name = ''

  if data == 'style_natgeo':
    settings['style'], settings['lang'], settings['slow'] = (
        'natgeo',
        'ar',
        True,
    )
    style_name = 'نبرة ناشيونال جيوغرافيك (الوثائقية)'
  elif data == 'style_military':
    settings['style'], settings['lang'], settings['slow'] = (
        'military',
        'ar',
        False,
    )
    style_name = 'النبرة العسكرية الرسمية'
  elif data == 'style_robot':
    settings['style'], settings['lang'], settings['slow'] = (
        'robot',
        'ar',
        False,
    )
    style_name = 'نبرة الروبوت الآلي'
  elif data == 'style_slow':
    settings['style'], settings['lang'], settings['slow'] = 'slow', 'ar', True
    style_name = 'القراءة البطيئة المفصلة'
  elif data == 'style_normal':
    settings['style'], settings['lang'], settings['slow'] = 'normal', 'ar', False
    style_name = 'النبرة العادية الافتراضية'

  bot.answer_callback_query(call.id, text='تم تحديث النبرة بنجاح')
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          f'تم اختيار: {style_name} بنجاح.\n\nالآن تفضل بإرسال النص المراد'
          ' تحويله وسيطبق عليه هذا الطابع فوراً.'
      ),
  )


# تحويل النص وهندسته بحسب النبرة المختارة
@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  chat_id = message.chat.id
  text_to_convert = message.text
  settings = get_settings(chat_id)

  if not text_to_convert.strip():
    bot.reply_to(message, 'الرجاء إرسال نص صالح لتحويله.')
    return

  style = settings.get('style', 'normal')
  processed_text = text_to_convert

  if style == 'natgeo':
    processed_text = (
        'في أعماق الطبيعة الساحرة ... وحيث تتكشف أسرار الكون ... '
        + text_to_convert
        + ' ... هكذا تستمر الحياة في كوكبنا.'
    )
  elif style == 'military':
    processed_text = (
        'تنبيه عسكري هام. انصتوا للتعليمات التالية بدقة: '
        + text_to_convert
        + ' ... انتهى البيان.'
    )
  elif style == 'robot':
    processed_text = '. '.join(list(text_to_convert))
  else:
    processed_text = text_to_convert

  processing_msg = bot.reply_to(message, 'جاري هندسة وتحويل النص إلى صوت...')

  try:
    tts = gTTS(
        text=processed_text,
        lang=settings['lang'],
        tld='com',
        slow=settings['slow'],
    )
    audio_path = f'audio_{chat_id}.mp3'
    tts.save(audio_path)

    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
      with open(audio_path, 'rb') as audio:
        bot.send_voice(chat_id, audio)
    else:
      bot.reply_to(message, 'عذراً، حدث خطأ في توليد الملف الصوتي.')

    bot.delete_message(chat_id, processing_msg.message_id)
    if os.path.exists(audio_path):
      os.remove(audio_path)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ غير متوقع: {e}')


if __name__ == '__main__':
  print('TTS Bot with Advanced Styles is running...')
  bot.remove_webhook()
  bot.infinity_polling()
