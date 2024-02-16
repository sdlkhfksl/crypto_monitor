import requests
import time
from datetime import datetime, timedelta

# REPLACE WITH YOUR TELEGRAM BOT TOKEN AND CHAT ID
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'   # Replace with your actual Telegram bot token
TELEGRAM_CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'   # Replace with your actual Telegram chat ID

# Replace with your desired cryptocurrencies
CURRENCY_IDS = [
    'bitcoin',
    'dogecoin',
    'ethereum',
    'uniswap',
    'shiba-inu',
    'ripple',
    'binancecoin',
    'cardano',
    'worldcoin',  # Assuming 'worldcoin' is the correct ID as discussed earlier
    'solana',
    'avalanche-2',  # Assuming this is the correct ID for Avalanche
    'polkadot',
]

# Cryptocurrency price API URL (no need to change)
API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# Replace USER_ALERTS with your desired price change thresholds for each currency
USER_ALERTS = {
    # Example thresholds: replace these with your values
    'bitcoin': {'increase': 5, 'decrease': 5},
    'dogecoin': {'increase': 10, 'decrease': 10},
    'ethereum': {'increase': 3, 'decrease': 3},
    # Add other currencies with their thresholds
    'worldcoin': {'increase': 8, 'decrease': 7},
    # Add other currencies with their thresholds
}

# (The rest of the script does not require modification for basic functionality)
# Dictionary to store the price record
price_records = {currency: (None, None) for currency in CURRENCY_IDS}

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
        'parse_mode': 'HTML'
    }
    requests.post(url, data=data)

# Main function for monitoring and alerting
def main():
    # Initial price checks to establish baseline
    current_prices = get_crypto_prices()
    for currency in CURRENCY_IDS:
        price_records[currency] = (datetime.utcnow(), current_prices[currency])

    # Monitoring loop
    while True:
        try:
            # Fetch new prices
            new_prices = get_crypto_prices()
            now = datetime.utcnow()
            
            # Check each currency for price changes
            for currency in CURRENCY_IDS:
                price_record = price_records[currency]
                last_time, last_price = price_record
                current_price = new_prices[currency]
                time_diff = now - last_time
                
                # Checking the threshold values and whether the time since last notification is more than 5 minutes
                if time_diff.total_seconds() >= 300:
                    price_change_percentage = ((current_price - last_price) / last_price) * 100
                    increase_threshold = USER_ALERTS[currency]['increase']
                    decrease_threshold = USER_ALERTS[currency]['decrease']
                    
                    # Send alert if the thresholds are crossed
                    if price_change_percentage >= increase_threshold:
                        message = f"{currency.upper()} price increased by {price_change_percentage:.2f}% in last 5 minutes. Current price: ${current_price}"
                        send_telegram_message(message)
                    elif price_change_percentage <= -decrease_threshold:
                        message = f"{currency.upper()} price decreased by {-price_change_percentage:.2f}% in last 5 minutes. Current price: ${current_price}"
                        send_telegram_message(message)
                    
                    # Update price record
                    price_records[currency] = (now, current_price)
            
            # Wait for a minute before checking again
            time.sleep(60)
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(60)

# Run the main monitoring function
if __name__ == '__main__':
    main()
