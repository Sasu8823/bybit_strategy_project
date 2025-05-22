import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class AdvancedStrategy:
    def __init__(self, symbols: List[str], initial_balance: float = 10000):
        self.symbols = symbols
        self.initial_balance = initial_balance
        self.positions: Dict[str, float] = {symbol: 0 for symbol in symbols}
        self.balances: Dict[str, List[float]] = {symbol: [initial_balance/len(symbols)] for symbol in symbols}
        self.fee_rate = 0.0012  # 0.12% per round trip
        
        # Risk management parameters
        self.max_position_size = 0.1  # Maximum 10% of balance per trade
        self.max_daily_trades = 5  # Maximum trades per day
        self.max_drawdown_limit = 0.15  # 15% maximum drawdown
        self.profit_taking_levels = [0.02, 0.05, 0.1]  # 2%, 5%, 10% profit taking levels
        self.stop_loss_levels = [0.01, 0.02, 0.03]  # 1%, 2%, 3% stop loss levels
        
    def generate_sample_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Generate realistic sample OHLCV data"""
        dates = pd.date_range(start=start_date, end=end_date, freq='1H')
        
        # Base prices and volatility for each symbol
        base_config = {
            'BTC-USD': {'price': 30000, 'vol': 0.02, 'trend': 0.0001},
            'ETH-USD': {'price': 2000, 'vol': 0.025, 'trend': 0.0002},
            'SOL-USD': {'price': 100, 'vol': 0.03, 'trend': 0.0003},
            'XRP-USD': {'price': 0.5, 'vol': 0.035, 'trend': 0.0004}
        }
        
        config = base_config.get(symbol, {'price': 100, 'vol': 0.02, 'trend': 0.0001})
        
        # Generate more realistic price movements
        np.random.seed(hash(symbol) % 100)
        
        # Add market regime changes
        regime_changes = np.random.choice([-1, 1], size=len(dates), p=[0.4, 0.6])
        regime = np.cumsum(regime_changes)
        
        # Generate returns with regime-dependent volatility
        returns = np.random.normal(
            config['trend'] * regime,
            config['vol'] * (1 + 0.5 * np.sin(np.arange(len(dates)) / 100))  # Cyclical volatility
        )
        
        # Add market impact and mean reversion
        returns = returns * (1 - 0.1 * np.abs(np.cumsum(returns)) / np.max(np.abs(np.cumsum(returns))))
        
        # Calculate prices
        prices = config['price'] * (1 + returns).cumprod()
        
        # Add realistic spreads
        spread = prices * 0.001  # 0.1% spread
        
        # Create OHLCV data
        data = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.002, len(dates)))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.002, len(dates)))),
            'close': prices,
            'volume': np.random.lognormal(10, 1, len(dates))
        }, index=dates)
        
        return data
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        df['bb_upper'] = ta.volatility.bollinger_hband(df['close'], window=20, window_dev=2)
        df['bb_middle'] = ta.volatility.bollinger_mavg(df['close'], window=20)
        df['bb_lower'] = ta.volatility.bollinger_lband(df['close'], window=20, window_dev=2)
        
        # ATR
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on multiple indicators"""
        df['signal'] = 0
        
        # RSI conditions
        rsi_oversold = df['rsi'] < 30
        rsi_overbought = df['rsi'] > 70
        
        # MACD conditions
        macd_bullish = (df['macd'] > df['macd_signal']) & (df['macd_diff'] > 0)
        macd_bearish = (df['macd'] < df['macd_signal']) & (df['macd_diff'] < 0)
        
        # Bollinger Bands conditions
        bb_oversold = df['close'] < df['bb_lower']
        bb_overbought = df['close'] > df['bb_upper']
        
        # Generate signals
        df.loc[rsi_oversold & macd_bullish & bb_oversold, 'signal'] = 1  # Buy signal
        df.loc[rsi_overbought & macd_bearish & bb_overbought, 'signal'] = -1  # Sell signal
        
        return df
    
    def backtest(self, start_date: str, end_date: str) -> Dict:
        """Run backtest with realistic constraints"""
        results = {}
        
        for symbol in self.symbols:
            try:
                print(f"\nProcessing {symbol}...")
                # Generate sample data
                df = self.generate_sample_data(symbol, 
                                             datetime.strptime(start_date, '%Y-%m-%d'),
                                             datetime.strptime(end_date, '%Y-%m-%d'))
                
                if df.empty:
                    print(f"No data available for {symbol}")
                    continue
                
                # Calculate indicators and signals
                df = self.calculate_indicators(df)
                df = self.generate_signals(df)
                
                # Initialize tracking variables
                balance = self.initial_balance / len(self.symbols)
                position = 0
                entry_price = 0
                trailing_stop = 0
                daily_trades = 0
                last_trade_date = None
                max_balance = balance
                current_drawdown = 0
                
                # Track trades and equity
                trades = []
                equity_curve = [balance]
                
                for i in range(1, len(df)):
                    current_price = df['close'].iloc[i]
                    current_date = df.index[i].date()
                    signal = df['signal'].iloc[i-1]
                    
                    # Reset daily trade counter
                    if last_trade_date != current_date:
                        daily_trades = 0
                        last_trade_date = current_date
                    
                    # Update drawdown
                    max_balance = max(max_balance, balance)
                    current_drawdown = (max_balance - balance) / max_balance
                    
                    # Check drawdown limit
                    if current_drawdown > self.max_drawdown_limit:
                        signal = -position  # Close position if drawdown limit reached
                    
                    # Update trailing stop if in position
                    if position != 0:
                        if position == 1:  # Long position
                            trailing_stop = max(trailing_stop, current_price - 2 * df['atr'].iloc[i])
                            if current_price < trailing_stop:
                                signal = -1  # Exit long
                        else:  # Short position
                            trailing_stop = min(trailing_stop, current_price + 2 * df['atr'].iloc[i])
                            if current_price > trailing_stop:
                                signal = 1  # Exit short
                    
                    # Execute trades with constraints
                    if signal != 0 and daily_trades < self.max_daily_trades:
                        if signal == 1 and position <= 0:  # Enter long
                            position = 1
                            entry_price = current_price
                            trailing_stop = entry_price - 2 * df['atr'].iloc[i]
                            balance *= (1 - self.fee_rate/2)
                            daily_trades += 1
                            trades.append({
                                'type': 'long',
                                'entry': entry_price,
                                'time': df.index[i]
                            })
                        
                        elif signal == -1 and position >= 0:  # Enter short
                            position = -1
                            entry_price = current_price
                            trailing_stop = entry_price + 2 * df['atr'].iloc[i]
                            balance *= (1 - self.fee_rate/2)
                            daily_trades += 1
                            trades.append({
                                'type': 'short',
                                'entry': entry_price,
                                'time': df.index[i]
                            })
                    
                    # Update balance with realistic constraints
                    if position != 0:
                        pnl = (current_price - entry_price) / entry_price * position
                        # Apply profit taking and stop loss
                        if pnl > 0:
                            for level in self.profit_taking_levels:
                                if pnl > level:
                                    pnl = level
                                    break
                        else:
                            for level in self.stop_loss_levels:
                                if -pnl > level:
                                    pnl = -level
                                    break
                        
                        # Limit the maximum return per trade
                        pnl = np.clip(pnl, -0.1, 0.1)  # Maximum 10% return per trade
                        balance *= (1 + pnl)
                    
                    equity_curve.append(balance)
                
                # Calculate performance metrics
                equity_curve = np.array(equity_curve)
                returns = np.diff(equity_curve) / equity_curve[:-1]
                
                # Calculate Sharpe ratio with proper error handling
                if len(returns) > 0 and returns.std() > 0:
                    sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
                else:
                    sharpe_ratio = 0
                
                results[symbol] = {
                    'final_balance': balance,
                    'return': (balance / (self.initial_balance/len(self.symbols)) - 1) * 100,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': 100 * (1 - equity_curve / np.maximum.accumulate(equity_curve)).max(),
                    'num_trades': len(trades),
                    'equity_curve': equity_curve,
                    'trades': trades
                }
                
            except Exception as e:
                print(f"Error processing {symbol}: {str(e)}")
                continue
        
        return results
    
    def plot_results(self, results: Dict):
        """Plot backtest results"""
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        
        plt.figure(figsize=(15, 10))
        
        # Plot equity curves
        plt.subplot(2, 1, 1)
        for symbol, result in results.items():
            plt.plot(result['equity_curve'], label=symbol)
        plt.title('Equity Curves')
        plt.xlabel('Time')
        plt.ylabel('Balance')
        plt.legend()
        plt.grid(True)
        
        # Plot drawdowns
        plt.subplot(2, 1, 2)
        for symbol, result in results.items():
            equity_curve = result['equity_curve']
            drawdown = 100 * (1 - equity_curve / np.maximum.accumulate(equity_curve))
            plt.plot(drawdown, label=symbol)
        plt.title('Drawdowns')
        plt.xlabel('Time')
        plt.ylabel('Drawdown (%)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('results/backtest_results.png')
        plt.close()

if __name__ == "__main__":
    # Initialize strategy
    symbols = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD']
    strategy = AdvancedStrategy(symbols)
    
    # Run backtest
    results = strategy.backtest('2023-01-01', '2023-12-31')
    
    # Print results
    for symbol, result in results.items():
        print(f"\n{symbol} Performance:")
        print(f"Final Return: {result['return']:.2f}%")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"Number of Trades: {result['num_trades']}")
    
    # Plot results
    strategy.plot_results(results)