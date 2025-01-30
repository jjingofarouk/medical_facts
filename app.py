from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the Telegram Bot Token from the environment
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize the application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Command to start the bot and display a welcome message
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Welcome to MedBot! Type /fact to get a medical fact.')

# Command to send a random medical fact
async def fact(update: Update, context: CallbackContext):
    medical_facts = [
        "Did you know? The human brain generates about 23 watts of power while awake.",
        "A single human blood cell takes about 60 seconds to make a complete circuit of the body.",
        "The human nose can detect more than 1 trillion different scents.",
        "The human body contains around 37.2 trillion cells."
    ]
    fact = medical_facts[0]  # Get the first fact for now; can be randomized later
    await update.message.reply_text(fact)

# Set up command handlers
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('fact', fact))

# Start the bot
if __name__ == '__main__':
    application.run_polling()
