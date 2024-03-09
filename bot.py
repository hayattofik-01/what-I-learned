import json
import os
from sched import scheduler
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from collections import defaultdict
from datetime import time
import requests

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
TOKEN = os.environ.get('TOKEN')
bot = Bot(token=TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Dictionary to store user IDs and their message counts
user_message_counts = defaultdict(int)

# Define a command handler function to generate leaderboards
def leaderboard(update, context):
    leaderboard_info = "🏆 Leaderboard 🏆\n\n"
    sorted_user_message_counts = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (user_id, count) in enumerate(sorted_user_message_counts, start=1):
        user = bot.get_chat_member(update.message.chat_id, user_id).user
        username = user.username if user.username else user.first_name
        leaderboard_info += f"👤 {username}: {count}\n"
        if i % 5 == 0:
            leaderboard_info += "\n"  # Add a newline every 5 entries
    update.message.reply_text(leaderboard_info)

# Define a message handler function
def handle_message(update, context):
    message = update.message.text
    user_id = update.message.from_user.id
    
    # Check if the message starts with "what I learned today"
    if message.startswith("what I learned today"):
        user_message_counts[user_id] += 1

# Function to fetch a random sura from the Quran API
def get_random_sura():
    url = "https://api.quran.com/api/v4/verses/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        verse_info = data.get("verse", {})
        verse_key = verse_info.get("verse_key", "")
        page_number = verse_info.get("page_number", "")
        juz_number = verse_info.get("juz_number", "")
        
        sura_info = (
            f"📜 *Verse Key:* `{verse_key}`\n"
            f"📖 *Page Number:* `{page_number}`\n"
            f"📚 *Juz Number:* `{juz_number}`\n\n"
            "🌟 *Read Allah's message:*\n"
            "Keep your heart open and your mind receptive as you delve into the wisdom and guidance "
            "of the Quran. Each verse holds a treasure of knowledge and inspiration waiting to be "
            "unveiled. Embrace the journey of learning and enlightenment with an open heart and a "
            "seeking spirit."
        )
        return sura_info
    else:
        return "Failed to fetch sura. Please try again later."

# Define a command handler for the Quran sura command
def quran_sura(update, context):
    sura_info = get_random_sura()
    update.message.reply_text(sura_info)

# Define a function to send the reminder message
def send_reminder():
    chat_id = "-1001913947795"  # Replace with your group's chat ID
    reminder_message = (
        "🕌 *Islamic Reminder* 🕌\n\n"
        "As-salamu alaykum! 🌟 It's time for the daily reminder.\n\n"
        "📌 *Reminder:* Don't forget to reflect on what you learned today!\n"
        "May Allah bless your efforts in seeking knowledge and understanding. 🙏"
    )  
    bot.send_message(chat_id=chat_id, text=reminder_message, parse_mode="MarkdownV2")

# Function to start the reminder job
def start_reminder_job():
    # Schedule the daily reminder job at 9:00 AM local time
    scheduler.every().day.at("09:00").do(send_reminder)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, bot)
    dispatcher.process_update(update)
    return jsonify({'status': 'ok'})

# Register the command handlers
dispatcher.add_handler(CommandHandler("quranaya", quran_sura))
dispatcher.add_handler(CommandHandler("leaderboard", leaderboard))

# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)
