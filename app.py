from flask import Flask, request
from telegram import Bot, Update
import os
import asyncio
from shazamio import Shazam
import yt_dlp

# 🔹 توکن ربات تلگرام
TOKEN = '7653985915:AAHplpzT0LoVhpesrG_DkrNx4TxbycoPnP0'
WEBHOOK_URL = 'https://telegram-bot-qe84.onrender.com/webhook'

# 🔹 تنظیمات اولیه
app = Flask(__name__)
bot = Bot(token=TOKEN)

# 📌 تابع دانلود ویدئو از اینستاگرام
def download_instagram_video(url):
    os.system(f"yt-dlp {url} -o video.mp4")

# 📌 استخراج صوت از ویدئو
def extract_audio():
    os.system("ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3")

# 📌 شناسایی موسیقی با Shazam
async def identify_song():
    shazam = Shazam()
    result = await shazam.recognize_song("audio.mp3")
    return result

# 📌 دانلود آهنگ از یوتیوب با yt-dlp
def download_song(song_name, artist):
    search_query = f"{song_name} {artist} official audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'song.mp3',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"ytsearch:{search_query}", download=True)

# 📌 تنظیم Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    asyncio.run(handle_message(update))
    return "ok"

# 📌 مدیریت پیام‌ها
async def handle_message(update):
    message = update.message
    text = message.text

    if "/y" in text:
        url = text.split(" ")[0]
        download_instagram_video(url)
        extract_audio()
        result = await identify_song()

        try:
            track = result['track']['title']
            artist = result['track']['subtitle']

            bot.send_message(chat_id=message.chat_id, text=f"🎵 آهنگ: {track}\n👤 خواننده: {artist}\nدر حال دانلود آهنگ... 🎶")

            download_song(track, artist)
            bot.send_audio(chat_id=message.chat_id, audio=open("song.mp3", "rb"))
        
        except KeyError:
            bot.send_message(chat_id=message.chat_id, text="متاسفم، نتونستم آهنگ رو پیدا کنم.")

# 📌 اجرای برنامه در Render
if __name__ == '__main__':
    bot.set_webhook(WEBHOOK_URL)
    app.run(host='0.0.0.0', port=5000)
