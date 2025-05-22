import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Parameters
initial_balance = 10000
period_days = 365  # 1 year
expected_daily_return = 0.01  # 1% per day

# Generate date range
start_date = datetime.today() - timedelta(days=period_days)
dates = pd.date_range(start=start_date, periods=period_days, freq='D')

# Simulate equity curve (compounding 1% per day)
balances = [initial_balance]
for _ in range(1, period_days):
    balances.append(balances[-1] * (1 + expected_daily_return))

# Create DataFrame
results = pd.DataFrame({'date': dates, 'balance': balances})
results.set_index('date', inplace=True)

# Calculate drawdown
results['cummax'] = results['balance'].cummax()
results['drawdown'] = 100 * (1 - results['balance'] / results['cummax'])

# Calculate performance metrics
final_return = (results['balance'].iloc[-1] / initial_balance - 1) * 100
max_drawdown = results['drawdown'].max()
daily_returns = results['balance'].pct_change().dropna()
sharpe_ratio = np.sqrt(252) * daily_returns.mean() / daily_returns.std() if daily_returns.std() > 0 else 0

# Print summary
print(f"Initial Balance: ${initial_balance:,.2f}")
print(f"Final Balance: ${results['balance'].iloc[-1]:,.2f}")
print(f"Final Return: {final_return:.2f}%")
print(f"Max Drawdown: {max_drawdown:.2f}%")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# Plot equity curve
plt.figure(figsize=(12,6))
plt.plot(results.index, results['balance'], label='Equity Curve')
plt.title('Simulated 1% Daily Compounding')
plt.xlabel('Date')
plt.ylabel('Balance')
plt.legend()
plt.tight_layout()
plt.savefig('results/1pct_per_day_equity_curve.png')
plt.close()
