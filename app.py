from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
import logging
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext

# Load environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY')  # Your Football-Data.org API key
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # URL where your app is hosted (e.g., https://your-app.onrender.com)

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)
dispatcher = Dispatcher(bot, None, workers=0)

# Command: Start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to Football Matches Bot! ⚽\n"
        "Use /matches to see today's matches.\n"
        "Use /standings to see league standings.\n"
        "Use /help for more info."
    )

# Command: Help
def help(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/matches - Show today's matches\n"
        "/standings [competition_code] - Show league standings (e.g., /standings PL)\n"
        "/help - Show this help message"
    )

# Command: Fetch and display today's matches
def matches(update: Update, context: CallbackContext):
    try:
        # Get today's date in the required format (YYYY-MM-DD)
        today = datetime.today().strftime('%Y-%m-%d')

        # Fetch matches from the API
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        params = {"dateFrom": today, "dateTo": today}
        response = requests.get(f"https://api.football-data.org/v4/matches", headers=headers, params=params)

        if response.status_code != 200:
            update.message.reply_text("Failed to fetch match data. Please try again later.")
            return

        matches_data = response.json().get("matches", [])

        if not matches_data:
            update.message.reply_text("No matches today. Check back tomorrow!")
            return

        # Format the matches into a readable message
        message = "Today's matches:\n\n"
        for match in matches_data:
            home_team = match["homeTeam"]["name"]
            away_team = match["awayTeam"]["name"]
            kickoff_time = datetime.fromisoformat(match["utcDate"]).strftime('%H:%M')
            competition = match["competition"]["name"]
            status = match["status"]
            score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}" if match['score']['fullTime'] else "0 - 0"
            message += f"⚽ {home_team} vs {away_team}\n"
            message += f"🏆 {competition}\n"
            message += f"⏰ {kickoff_time} UTC\n"
            message += f"📊 {score} ({status})\n\n"

        update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        update.message.reply_text("An error occurred. Please try again later.")

# Command: Fetch and display league standings
def standings(update: Update, context: CallbackContext):
    try:
        # Get the competition code from the command (e.g., /standings PL)
        if not context.args:
            update.message.reply_text("Please specify a competition code (e.g., /standings PL).")
            return

        competition_code = context.args[0].upper()

        # Fetch standings from the API
        headers = {"X-Auth-Token": FOOTBALL_API_KEY}
        response = requests.get(f"https://api.football-data.org/v4/competitions/{competition_code}/standings", headers=headers)

        if response.status_code != 200:
            update.message.reply_text("Failed to fetch standings. Please check the competition code and try again.")
            return

        standings_data = response.json().get("standings", [])

        if not standings_data:
            update.message.reply_text("No standings found for this competition.")
            return

        # Format the standings into a readable message
        message = f"Standings for {competition_code}:\n\n"
        for table in standings_data:
            if table["type"] == "TOTAL":
                for team in table["table"]:
                    position = team["position"]
                    team_name = team["team"]["name"]
                    points = team["points"]
                    played_games = team["playedGames"]
                    message += f"{position}. {team_name} - {points} pts ({played_games} games)\n"

        update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error fetching standings: {e}")
        update.message.reply_text("An error occurred. Please try again later.")

# Add command handlers to the dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("matches", matches))
dispatcher.add_handler(CommandHandler("standings", standings))
dispatcher.add_handler(CommandHandler("help", help))

# Webhook route for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify(success=True)

# Set webhook on startup
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    result = bot.set_webhook(url=webhook_url)
    return f"Webhook set: {result}"

# Health check route
@app.route('/health', methods=['GET'])
def health():
    return "OK"

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)