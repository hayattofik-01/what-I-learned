
import asyncio
import json
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from collections import defaultdict
from datetime import time
import requests

# Dictionary to store user IDs and their message counts
user_message_counts = defaultdict(int)

# Define a command handler function to generate leaderboards
def leaderboard(update, context):
    leaderboard_info = "🏆 Leaderboard 🏆\n\n"
    sorted_user_message_counts = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (user_id, count) in enumerate(sorted_user_message_counts, start=1):
        user = context.bot.get_chat_member(update.message.chat_id, user_id).user
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
async def get_random_sura():
    url = "https://api.quran.com/api/v4/verses/random"
    response = await asyncio.to_thread(requests.get, url)
    if response.status_code == 200:
        data = json.loads(response.content.decode("utf-8"))
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
    async def async_quran_sura():
        sura_info = await get_random_sura()
        update.message.reply_text(sura_info)

    asyncio.run(async_quran_sura())

# Define a function to send the reminder message
def send_reminder(context):
    chat_id = "-1001913947795"  # Replace with your group's chat ID
    reminder_message = (
        "🕌 *Islamic Reminder* 🕌\n\n"
        "As-salamu alaykum! 🌟 It's time for the daily reminder.\n\n"
        "📌 *Reminder:* Don't forget to reflect on what you learned today!\n"
        "May Allah bless your efforts in seeking knowledge and understanding. 🙏"
    )  
    context.bot.send_message(chat_id=chat_id, text=reminder_message, parse_mode="MarkdownV2")

# Function to start the reminder job
def start_reminder_job(context):
    # Schedule the daily reminder job at 9:00 AM local time
    context.job_queue.run_daily(send_reminder, time(hour=1, minute=2, second=0))

def start(update, context):
    # Send As-salamu alaykum message
    update.message.reply_text("As-salamu alaykum! 🌟 Welcome to our Quran learning bot. Here are the available commands:")
    # Display the available commands as a menu
    menu = "📚 *Available Commands:*\n"
    menu += "/quranaya - Get a random Quran verse\n"
    menu += "/leaderboard - View the leaderboard\n"
  
    update.message.reply_text(menu, parse_mode="Markdown")

# Telegram bot token
TOKEN = os.environ.get('TOKEN')

# Create an Updater and pass it your bot's token
updater = Updater(token= TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Register the command handlers
dispatcher.add_handler(CommandHandler("quranaya", quran_sura))
dispatcher.add_handler(CommandHandler("leaderboard", leaderboard))

dispatcher.add_handler(CommandHandler("start", start))

# Register the message handler
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C
updater.idle()
