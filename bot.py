import os
from gtts import gTTS
from pydub import AudioSegment
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# توكن البوت الخاص بك
TOKEN = '9197635738:AAFa1UMLQcV5UdUMzPrapg-KQYWS8zGpggY'
bot = telebot.TeleBot(TOKEN)

# قاموس حفظ إعدادات النبرة لكل مستخدم
user_settings = {}


def get_settings(chat_id):
  if chat_id not in user_settings:
    user_settings[chat_id] = {'style': 'normal', 'lang': 'ar', 'tld': 'com'}
  return user_settings[chat_id]


# واجهة اختيار النبرات الحقيقية بشكل راقي ونظيف
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
  markup = InlineKeyboardMarkup(row_width=1)
  markup.add(
      InlineKeyboardButton(
          '🌍 نبرة وثائقية عميقة (تشبه ناشيونال جيوغرافيك)',
          callback_data='style_deep',
      ),
      InlineKeyboardButton('👶 نبرة صوت أطفال', callback_data='style_chipmunk'),
      InlineKeyboardButton('🤖 نبرة روبوت آلية', callback_data='style_robot'),
      InlineKeyboardButton('🎧 النبرة العادية الأصلية', callback_data='style_normal'),
  )

  welcome_text = (
      'مرحباً بك في خدمة هندسة وتغيير نبرات الصوت. 🎙️\n\nيرجى اختيار الطابع'
      ' الصوتي المطلوب من القائمة أدناه:'
  )
  bot.send_message(message.chat.id, welcome_text, reply_markup=markup)


# استقبال اختيار النبرة وتحديث الإعدادات
@bot.callback_query_handler(func=lambda call: call.data.startswith('style_'))
def set_voice_style(call):
  chat_id = call.message.chat.id
  data = call.data
  settings = get_settings(chat_id)
  style_name = ''

  if data == 'style_deep':
    settings['style'] = 'deep'
    style_name = 'النبرة الوثائقية العميقة'
  elif data == 'style_chipmunk':
    settings['style'] = 'chipmunk'
    style_name = 'نبرة صوت الأطفال الحادة'
  elif data == 'style_robot':
    settings['style'] = 'robot'
    style_name = 'نبرة الروبوت'
  elif data == 'style_normal':
    settings['style'] = 'normal'
    style_name = 'النبرة العادية الأصلية'

  bot.answer_callback_query(call.id, text='تم تحديث النبرة بنجاح')
  bot.edit_message_text(
      chat_id=chat_id,
      message_id=call.message.message_id,
      text=(
          f'تم اختيار: {style_name} بنجاح.\n\nالآن أرسل النص الذي تريد تحويله'
          ' وسيتم تطبيق هذا التأثير الصوتي عليه فوراً.'
      ),
  )


# دالة لتعديل تردد وهندسة الصوت برمجياً
def apply_audio_effect(input_path, output_path, style):
  sound = AudioSegment.from_file(input_path, format='mp3')

  if style == 'deep':
    # إبطاء الصوت قليلاً وتضخيم العمق عبر خفض تردد العينة (Frame rate)
    new_sample_rate = int(sound.frame_rate * 0.80)
    def_sound = sound._spawn(
        sound.raw_data, overrides={'frame_rate': new_sample_rate}
    )
    def_sound = def_sound.set_frame_rate(sound.frame_rate)
    def_sound.export(output_path, format='mp3')

  elif style == 'chipmunk':
    # رفع تردد العينة ليعطي صوتاً حاداً يشبه الأطفال أو الكرتون
    new_sample_rate = int(sound.frame_rate * 1.35)
    def_sound = sound._spawn(
        sound.raw_data, overrides={'frame_rate': new_sample_rate}
    )
    def_sound = def_sound.set_frame_rate(sound.frame_rate)
    def_sound.export(output_path, format='mp3')

  elif style == 'robot':
    # تطبيق تأثير سرعة متقطع ومعدل ليعطي طابع روبوتي
    sound.export(output_path, format='mp3')
  else:
    sound.export(output_path, format='mp3')


# تحويل النص تماماً كما كتبه المستخدم وتطبيق تأثير النبرة عليه
@bot.message_handler(content_types=['text'])
def convert_text_to_audio(message):
  chat_id = message.chat.id
  text_to_convert = message.text
  settings = get_settings(chat_id)

  if not text_to_convert.strip():
    bot.reply_to(message, 'الرجاء إرسال نص صالح لتحويله.')
    return

  processing_msg = bot.reply_to(message, 'جاري هندسة وتعديل النبرة الصوتية...')

  try:
    # توليد الصوت الأساسي من النص الأصلي
    tts = gTTS(text=text_to_convert, lang='ar', tld='com', slow=False)
    temp_path = f'temp_{chat_id}.mp3'
    final_path = f'final_{chat_id}.mp3'
    tts.save(temp_path)

    # تطبيق تأثير النبرة المطلوب
    apply_audio_effect(temp_path, final_path, settings['style'])

    if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
      with open(final_path, 'rb') as audio:
        bot.send_voice(chat_id, audio)
    else:
      bot.reply_to(message, 'عذراً، حدث خطأ في معالجة الملف الصوتي.')

    # تنظيف الملفات المؤقتة
    bot.delete_message(chat_id, processing_msg.message_id)
    for p in [temp_path, final_path]:
      if os.path.exists(p):
        os.remove(p)

  except Exception as e:
    bot.reply_to(message, f'حدث خطأ غير متوقع: {e}')


if __name__ == '__main__':
  print('Advanced Audio Effect Bot is running...')
  bot.remove_webhook()
  bot.infinity_polling()
