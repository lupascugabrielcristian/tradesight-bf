import argparse
import sys
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

sys.path.append('src')

from strategy_lab.backtest import BacktestEngine


def create_sample_ohlcv(periods: int, seed: int) -> pd.DataFrame:
    np.random.seed(seed)
    dates = pd.date_range('2024-01-01', periods=periods, freq='D')
    prices = 100 + np.cumsum(np.random.randn(periods) * 0.8)
    return pd.DataFrame(
        {
            'open': prices * (1 + np.random.uniform(-0.005, 0.005, periods)),
            'high': prices * (1 + np.random.uniform(0.001, 0.02, periods)),
            'low': prices * (1 - np.random.uniform(0.001, 0.02, periods)),
            'close': prices,
            'volume': np.random.randint(1000, 10000, periods),
        },
        index=dates,
    )


def custom_strategy(data: pd.DataFrame, index: int, positions: List) -> Optional[Dict]:
    if index < 50:
        return None

    row = data.iloc[index]

    if row['rsi'] < 30 and row['close'] > row['sma_50'] and not positions:
        return {
            'action': 'buy',
            'size': 0.7,
            'stop_loss': row['close'] * 0.95,
            'take_profit': row['close'] * 1.1,
        }

    if row['rsi'] > 70 and positions:
        return {'action': 'close'}

    return None


def load_csv_ohlcv(csv_path: str, date_column: str) -> pd.DataFrame:
    data = pd.read_csv(csv_path)
    data.columns = [col.strip().lower() for col in data.columns]
    if date_column:
        normalized_date_col = date_column.strip().lower()
        if normalized_date_col in data.columns:
            data[normalized_date_col] = pd.to_datetime(data[normalized_date_col])
            data = data.set_index(normalized_date_col)
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"CSV missing required columns: {missing_cols}")
    data = data[required_cols].copy()
    for col in required_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data = data.dropna(subset=required_cols)
    if isinstance(data.index, pd.DatetimeIndex):
        data = data.sort_index()
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--asset', default='SAMPLE')
    parser.add_argument('--periods', type=int, default=300)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--csv', default='')
    parser.add_argument('--date-column', default='date')
    parser.add_argument('--initial-balance', type=float, default=500.0)
    parser.add_argument('--fee-rate', type=float, default=0.001)
    parser.add_argument('--slippage-pct', type=float, default=0.0005)
    args = parser.parse_args()

    if args.csv:
        data = load_csv_ohlcv(csv_path=args.csv, date_column=args.date_column)
    else:
        data = create_sample_ohlcv(periods=args.periods, seed=args.seed)

    engine = BacktestEngine(
        initial_balance=args.initial_balance,
        fee_rate=args.fee_rate,
        slippage_pct=args.slippage_pct,
    )

    result = engine.run_backtest(
        data=data,
        strategy_func=custom_strategy,
        asset_name=args.asset,
    )

    metrics = result['metrics']
    print(f"Asset: {result['asset_name']}")
    print(f"Rows used: {len(data)}")
    print(f"Initial balance: {args.initial_balance:.2f}")
    print(f"Final balance: {result['final_balance']:.2f}")
    print(f"Total trades: {metrics['total_trades']}")
    print(f"Win rate: {metrics['win_rate']:.2f}%")
    print(f"Total PnL %: {metrics['total_pnl_pct']:.2f}%")
    print(f"Sharpe ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"Max drawdown %: {metrics['max_drawdown_pct']:.2f}%")


if __name__ == '__main__':
    main()
