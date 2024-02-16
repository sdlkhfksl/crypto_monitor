import requests
import time
from datetime import datetime, timedelta

# REPLACE WITH YOUR TELEGRAM BOT TOKEN AND CHAT ID
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'    # Replace with your Telegram bot token
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'    # Replace with your Telegram chat ID

# Listed Cryptocurrencies (No change needed)
CURRENCY_IDS = [
    'bitcoin',
    'dogecoin',
    'ethereum',
    # ... the rest of your listed currencies ...
]

# Cryptocurrency price API URL (no need to change)
API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# Set price alert thresholds
PRICE_ALERTS = {
    'bitcoin': {'low': 10000, 'high': 60000, 'percent_change': 5},
    'dogecoin': {'low': 0.01, 'high': 0.50, 'percent_change': 10},
    # ... add your other currencies with their thresholds ...
}

# Dictionary to store the price record
price_records = {currency: {'last_checked': None, 'last_price': None} for currency in CURRENCY_IDS}

# Function to fetch current prices
def get_crypto_prices():
    ids = ','.join(CURRENCY_IDS)
    url = f"{API_URL}?ids={ids}&vs_currencies=usd"
    response = requests.get(url)
    prices = response.json()
    return {currency: prices[currency]['usd'] for currency in CURRENCY_IDS}

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=data)

# Main function for monitoring and alerting
def main():
    while True:
        try:
            # Fetch new prices
            current_prices = get_crypto_prices()
            now = datetime.utcnow()

            # Check each currency for price alerts and changes
            for currency in CURRENCY_IDS:
                price_info = price_records[currency]
                last_price = price_info['last_price']
                current_price = current_prices[currency]
                percent_change = 0
                send_message = False
                message = ""

                # Check percentage price change if we have a last price
                if last_price:
                    percent_change = ((current_price - last_price) / last_price) * 100
                    if abs(percent_change) >= PRICE_ALERTS[currency]['percent_change']:
                        direction = 'increased' if percent_change > 0 else 'decreased'
                        message += f"{currency.capitalize()} price has {direction} by {abs(percent_change):.2f}% over the last 5 minutes. "
                        send_message = True

                # Check if price is below the low alert threshold
                if current_price <= PRICE_ALERTS[currency]['low']:
                    message += f"Current price of {currency.capitalize()} is below the alert threshold at ${current_price:.2f}! "
                    send_message = True

                # Check if price is above the high alert threshold
                if current_price >= PRICE_ALERTS[currency]['high']:
                    message += f"Current price of {currency.capitalize()} is above the alert threshold at ${current_price:.2f}! "
                    send_message = True

                if send_message:
                    send_telegram_message(message)

                # Update last checked time and price
                price_info['last_checked'] = now
                price_info['last_price'] = current_price

            # Sleep for 5 minutes before the next check
            time.sleep(300)

        except Exception as e:
            print(f"An error occurred: {e}")
            # Sleep for a short time before retrying
            time.sleep(60)

# Run the main monitoring function
if __name__ == '__main__':
    main()
