import os
import requests
import time
from collections import deque
from datetime import datetime, timedelta

# Get the Telegram bot token and chat ID from environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# List of cryptocurrencies to monitor
CURRENCY_IDS = [
    'bitcoin',
    'dogecoin',
    'ethereum',
    'uniswap',
    'shiba-inu',
    'ripple',
    'binancecoin',
    'cardano',
    'worldcoin',
    'solana',
    'avalanche-2',
    'polkadot',
]

# Set up the price threshold alerts and percent change thresholds
PRICE_ALERTS = {
    'bitcoin': {'low': 20000, 'high': 60000, 'percent_change': 5},
    # ... add other currencies with their low, high, and percentage change thresholds ...
}

# Price API URL (CoinGecko as an example)
API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# Initialize price records with a deque to maintain a 5-minute window of price checks
price_data = {currency: deque(maxlen=5) for currency in CURRENCY_IDS}

# Function to fetch current prices
def get_crypto_prices(ids):
    query_params = {
        'ids': ','.join(ids),
        'vs_currencies': 'usd',
    }
    response = requests.get(API_URL, params=query_params)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Error fetching prices")

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise ValueError("Error sending message")

# Check the price change over the last 5 minutes
def check_price_change(currency, prices):
    if len(prices) == prices.maxlen:
        earliest_price = prices[0]['price']
        latest_price = prices[-1]['price']
        percent_change = (latest_price - earliest_price) / earliest_price * 100
        return percent_change
    return 0  # Not enough data to calculate change

# Function to check prices and notify if needed
def check_prices_and_notify():
    current_prices = get_crypto_prices(CURRENCY_IDS)

    for currency in CURRENCY_IDS:
        current_price = current_prices[currency]['usd']
        current_time = datetime.utcnow()
        
        # Check high and low thresholds
        if current_price <= PRICE_ALERTS[currency]['low']:
            send_telegram_message(f"{currency.upper()} price is below alert threshold: ${current_price}")
        elif current_price >= PRICE_ALERTS[currency]['high']:
            send_telegram_message(f"{currency.upper()} price is above alert threshold: ${current_price}")
        
        # Record the current price with timestamp
        price_data[currency].append({'time': current_time, 'price': current_price})
        
        # Calculate percentage change
        percent_change = check_price_change(currency, price_data[currency])
        if abs(percent_change) >= PRICE_ALERTS[currency]['percent_change']:
            send_telegram_message(f"{currency.upper()} price changed by {percent_change:.2f}% in the last 5 minutes")

# Main script function
def main():
    while True:
        try:
            check_prices_and_notify()
            time.sleep(60)  # Check every minute
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)  # Wait a minute and try again

if __name__ == '__main__':
    main()
