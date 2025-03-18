import sys
sys.path.insert(0, "libs")
from flask import Flask, request
import sys
sys.path.insert(0, "libs")
from telegram import Bot, Update
import sys
sys.path.insert(0, "libs")
import os
import sys
sys.path.insert(0, "libs")
import asyncio
import sys
sys.path.insert(0, "libs")
from shazamio import Shazam
import sys
sys.path.insert(0, "libs")
import yt_dlp

TOKEN = '7653985915:AAHplpzT0LoVhpesrG_DkrNx4TxbycoPnP0'
WEBHOOK_URL = 'https://errors.infinityfree.net/webhook'

app = Flask(__name__)
bot = Bot(token=TOKEN)

# تابع برای دانلود ویدئو از اینستاگرام
def download_instagram_video(url):
    os.system(f"yt-dlp {url} -o video.mp4")

# استخراج صوت از ویدئو
def extract_audio():
    os.system("ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3")

# شناسایی موسیقی با Shazam
def identify_song():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    shazam = Shazam()
    result = loop.run_until_complete(shazam.recognize_song("audio.mp3"))
    return result

# دانلود آهنگ از یوتیوب با yt-dlp
def download_song(song_name, artist):
    search_query = f"{song_name} {artist} official audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'song.mp3',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f"ytsearch:{search_query}", download=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    handle_message(update)
    return "ok"

# هندلر پیام‌ها
def handle_message(update):
    message = update.message
    text = message.text

    if "/y" in text:
        url = text.split(" ")[0]
        download_instagram_video(url)
        extract_audio()
        result = identify_song()

        try:
            track = result['track']['title']
            artist = result['track']['subtitle']
            message.reply_text(f"🎵 آهنگ: {track}\n👤 خواننده: {artist}\nدر حال دانلود آهنگ... 🎶")
            
            download_song(track, artist)
            message.reply_audio(audio=open("song.mp3", "rb"))
        
        except KeyError:
            message.reply_text("متاسفم، نتونستم آهنگ رو پیدا کنم.")

if __name__ == '__main__':
    bot.set_webhook(WEBHOOK_URL)
    app.run(host='0.0.0.0', port=5000)
