import logging
import os
import threading
from flask import Flask
import requests

from dotenv import load_dotenv

from plugin_manager import PluginManager
from openai_helper import OpenAIHelper, default_max_tokens, are_functions_available
from telegram_bot import ChatGPTTelegramBot

from usage_tracker import UsageTracker

app = Flask(__name__)

# This route will be used to keep the bot alive
@app.route('/')
def index():
    return 'Bot is alive!'

def keep_alive():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    while True:
        try:
            response = requests.get(f"{os.environ.get('BOT_URL', 'http://localhost:5000')}")
            if response.status_code == 200:
                print("Bot is alive.")
            else:
                print(f"Unexpected response status: {response.status_code}")
        except Exception as error:
            print(f"Failed to maintain bot activity: {error}")
        # Sleep for 5 minutes
        import time
        time.sleep(300)

def main():
    # Read .env file
    load_dotenv()
    first_admin = os.environ.get('ADMIN_USER_IDS','0').split(',')[0]
    admin_tracker = UsageTracker(user_id=first_admin, username='admin',chat_id=first_admin ,default_max_tokens=default_max_tokens,are_functions_available=are_functions_available)
    users_directory = admin_tracker.logs_dir

    # Setup logging
    logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("logs.log", mode="a"),  # Append to the file
        logging.StreamHandler()  # Optional: log to console as well
            ])

    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Check if the required environment variables are set
    required_values = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
    missing_values = [value for value in required_values if os.environ.get(value) is None]
    if len(missing_values) > 0:
        logging.error(f'The following environment values are missing in your .env: {", ".join(missing_values)}')
        exit(1)

    # Setup configurations
    model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini-2024-07-18')
    functions_available = are_functions_available(model=model)
    max_tokens_default = default_max_tokens(model=model)

    enable_functions = os.environ.get('ENABLE_FUNCTIONS', str(functions_available)).lower() == 'true'
    if enable_functions and not functions_available:
        logging.error(f'ENABLE_FUNCTIONS is set to true, but the model {model} does not support it. '
                        'Please set ENABLE_FUNCTIONS to false or use a model that supports it.')
        exit(1)
    if os.environ.get('MONTHLY_USER_BUDGETS') is not None:
        logging.warning('The environment variable MONTHLY_USER_BUDGETS is deprecated. '
                        'Please use USER_BUDGETS with BUDGET_PERIOD instead.')
    if os.environ.get('MONTHLY_GUEST_BUDGET') is not None:
        logging.warning('The environment variable MONTHLY_GUEST_BUDGET is deprecated. '
                        'Please use GUEST_BUDGET with BUDGET_PERIOD instead.')

    plugin_config = {
        'plugins': os.environ.get('PLUGINS', '').split(',')
    }

    # Setup and run ChatGPT and Telegram bot
    plugin_manager = PluginManager(config=plugin_config)
    openai_helper = OpenAIHelper(plugin_manager=plugin_manager)
    telegram_bot = ChatGPTTelegramBot(openai=openai_helper)

    # Start Flask server in a separate thread
    threading.Thread(target=keep_alive).start()

    telegram_bot.run()

if __name__ == '__main__':
    main()
