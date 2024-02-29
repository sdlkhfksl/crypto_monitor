import os
import requests
import time
import logging
from collections import deque
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    handlers=[logging.FileHandler('crypto_monitor.log'),
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)
# ... 保留此部分中其它定义不变 ...

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # This will raise an HTTPError if the response was an error
        logger.info(f"Message sent: {message}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Error sending message: {e.response.content}")
    except Exception as e:
        logger.error(f"Unhandled exception during sending message: {e}")

# Main script function
def main():
    while True:
        try:
            check_prices_and_notify()
            logger.info("Sleeping for 60 seconds")
            time.sleep(60)  # Check every minute
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            # When an exception happens, we still want to pause before retrying
            logger.info("Exception encountered. Sleeping for 60 seconds before retry.")
            time.sleep(60)

if __name__ == '__main__':
    main()
