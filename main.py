import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample OHLCV data for BTCUSDT"""
    # Create date range for the last 1000 hours
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=1000)
    dates = pd.date_range(start=start_date, end=end_date, freq='1H')
    
    # Generate random price movements
    np.random.seed(42)  # For reproducibility
    base_price = 30000  # Starting price
    returns = np.random.normal(0.0001, 0.02, len(dates))  # Random returns
    prices = base_price * (1 + returns).cumprod()
    
    # Create OHLCV data
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.002, len(dates)))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.002, len(dates)))),
        'close': prices,
        'volume': np.random.lognormal(10, 1, len(dates))
    })
    
    return data

def run_strategy():
    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)
    os.makedirs('data', exist_ok=True)

    # Generate or load data
    data_path = 'data/BTCUSDT_1h.csv'
    if not os.path.exists(data_path):
        print("Generating sample data...")
        df = generate_sample_data()
        df.to_csv(data_path, index=False)
    else:
        print("Loading existing data...")
        df = pd.read_csv(data_path)

    # Convert timestamp to datetime and set as index
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    # Calculate indicators
    df['ema'] = ta.trend.ema_indicator(df['close'], window=20)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)

    # Define entry/exit logic
    df['signal'] = 0
    df.loc[(df['close'] > df['ema']) & (df['rsi'] > 50), 'signal'] = 1  # Buy
    df.loc[(df['close'] < df['ema']) & (df['rsi'] < 50), 'signal'] = -1  # Sell

    # Simulate trades (compounding, with fees)
    initial_balance = 1000
    balance = initial_balance
    position = 0
    fee_rate = 0.0012  # 0.12% per round trip

    returns = []
    entry_price = 0

    for i in range(1, len(df)):
        if df['signal'].iloc[i-1] == 1 and position == 0:
            position = 1
            entry_price = df['close'].iloc[i]
            balance *= (1 - fee_rate/2)
        elif df['signal'].iloc[i-1] == -1 and position == 1:
            position = 0
            exit_price = df['close'].iloc[i]
            pnl = (exit_price - entry_price) / entry_price
            balance *= (1 + pnl) * (1 - fee_rate/2)
        returns.append(balance)

    df = df.iloc[1:]
    df['balance'] = returns

    # Plot results
    plt.figure(figsize=(12,6))
    plt.plot(df.index, df['balance'], label='Equity Curve')
    plt.title('Backtest Result')
    plt.xlabel('Time')
    plt.ylabel('Balance')
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/equity_curve.png')
    plt.show()

    # Calculate and print summary stats
    final_return = (balance / initial_balance - 1) * 100
    max_drawdown = 100 * (1 - df['balance'] / df['balance'].cummax()).max()
    num_trades = int(df['signal'].diff().abs().sum() // 2)

    print("\nStrategy Performance Summary:")
    print(f"Initial Balance: ${initial_balance:,.2f}")
    print(f"Final Balance: ${balance:,.2f}")
    print(f"Final Return: {final_return:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Number of Trades: {num_trades}")

if __name__ == "__main__":
    run_strategy()