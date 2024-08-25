import ccxt
import numpy as np
import pandas as pd
import time
import requests
from datetime import datetime, timedelta

# Telegram Bot Constants
BOT_TOKEN = '7087052045:AAF3eJLHSvBGKtqqa2l_e7su_ESiteL8ai8'
CHAT_ID = '1640026631'

# 加密货币交易对列表
SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT',
           'TRX/USDT', 'AVAX/USDT', 'SHIB/USDT', 'LINK/USDT', 'DOT/USDT', 'UNI/USDT', 'TON/USDT', 'WLD/USDT']

# 初始化Coinbase交易所
EXCHANGE = ccxt.coinbase()

# 用于存储每个交易对的上一次后验概率
previous_posterior_up = {symbol: None for symbol in SYMBOLS}

# 计算 EMA
def ema(series, length):
    return series.ewm(span=length, adjust=False).mean()

# 计算 SMA
def sma(series, length):
    return series.rolling(window=length).mean()

# 计算 DEMA
def dema(series, length):
    ema1 = ema(series, length)
    ema2 = ema(ema1, length)
    return 2 * ema1 - ema2

# 计算 VWMA
def vwma(series, volume, length):
    return (series * volume).rolling(window=length).sum() / volume.rolling(window=length).sum()

# 获取历史数据
def get_data(symbol, timeframe='1h', limit=100):
    bars = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# 发送Telegram消息
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': message}
    response = requests.get(url, params=params)
    return response.json()

# 计算后验概率
def calculate_posterior_up(ema, sma, dema, vwma, ema_fast, sma_fast, dema_fast, vwma_fast):
    def sig(src, gap):
        result = [1 if src[i] >= src[i-gap] else 0 for i in range(gap, len(src))]
        return sum(result) / len(result) if result else 0
    
    ema_trend = sig(ema, 10)
    sma_trend = sig(sma, 10)
    dema_trend = sig(dema, 10)
    vwma_trend = sig(vwma, 10)

    ema_trend_fast = sig(ema_fast, 10)
    sma_trend_fast = sig(sma_fast, 10)
    dema_trend_fast = sig(dema_fast, 10)
    vwma_trend_fast = sig(vwma_fast, 10)
    
    prior_up = (ema_trend + sma_trend + dema_trend + vwma_trend) / 4
    prior_down = 1 - prior_up

    likelihood_up = (ema_trend_fast + sma_trend_fast + dema_trend_fast + vwma_trend_fast) / 4
    likelihood_down = 1 - likelihood_up

    posterior_up = prior_up * likelihood_up / (prior_up * likelihood_up + prior_down * likelihood_down)
    
    if posterior_up is None:
        posterior_up = 0
    
    return posterior_up

# 检查并发送通知
def check_and_notify():
    for symbol in SYMBOLS:
        df = get_data(symbol.replace('/', '-'))
        close = df['close']
        volume = df['volume']

        # 计算移动平均线
        ema_values = ema(close, 60)
        sma_values = sma(close, 60)
        dema_values = dema(close, 60)
        vwma_values = vwma(close, volume, 60)

        ema_fast_values = ema(close, 40)
        sma_fast_values = sma(close, 40)
        dema_fast_values = dema(close, 40)
        vwma_fast_values = vwma(close, volume, 40)

        # 计算当前的后验概率
        posterior_up = calculate_posterior_up(ema_values, sma_values, dema_values, vwma_values,
                                              ema_fast_values, sma_fast_values, dema_fast_values, vwma_fast_values)
        
        # 获取上一次的后验概率
        prev_posterior_up = previous_posterior_up[symbol]

        # 判断是否发送消息
        if prev_posterior_up is not None:
            # 检测交叉 0.5 的情况
            if prev_posterior_up < 0.5 and posterior_up > 0.5:
                message = (f"Symbol: {symbol}\n"
                           f"EMA: {ema_values.iloc[-1]:.2f}\n"
                           f"SMA: {sma_values.iloc[-1]:.2f}\n"
                           f"DEMA: {dema_values.iloc[-1]:.2f}\n"
                           f"VWMA: {vwma_values.iloc[-1]:.2f}\n"
                           f"Probability of Up Trend: {posterior_up*100:.2f}%\n"
                           f"Condition: Entering Uptrend")
                send_telegram_message(message)
            elif prev_posterior_up > 0.5 and posterior_up < 0.5:
                message = (f"Symbol: {symbol}\n"
                           f"EMA: {ema_values.iloc[-1]:.2f}\n"
                           f"SMA: {sma_values.iloc[-1]:.2f}\n"
                           f"DEMA: {dema_values.iloc[-1]:.2f}\n"
                           f"VWMA: {vwma_values.iloc[-1]:.2f}\n"
                           f"Probability of Down Trend: {100 - posterior_up*100:.2f}%\n"
                           f"Condition: Entering Downtrend")
                send_telegram_message(message)

        # 更新前一次的后验概率
        previous_posterior_up[symbol] = posterior_up

        # 控制 API 请求频率，每次请求之间等待 5 秒
        time.sleep(5)

# 主函数，每 1 小时运行一次检查，在每个小时开头启动
def main():
    while True:
        # 计算下一次运行的时间点（每个小时的开始）
        now = datetime.now()
        next_run = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        wait_time = (next_run - now).total_seconds()

        # 等待到下一个整点
        time.sleep(wait_time)

        # 进行检查和发送通知
        check_and_notify()

if __name__ == '__main__':
    main()
