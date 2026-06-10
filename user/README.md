# Custom Backtest Script

This folder contains a ready-to-run script for backtesting a custom strategy:

- `run_custom_backtest.py`

## What the script does

- Uses `BacktestEngine` from `src/strategy_lab/backtest.py`
- Runs a custom RSI + SMA strategy (`custom_strategy` in the script)
- Prints key results:
  - final balance
  - total trades
  - win rate
  - total PnL %
  - sharpe ratio
  - max drawdown %

## Run with generated sample data

```bash
python3 user/run_custom_backtest.py --asset SPY --periods 320
```

Optional parameters:

```bash
python3 user/run_custom_backtest.py \
  --asset SPY \
  --periods 300 \
  --seed 42 \
  --initial-balance 500 \
  --fee-rate 0.001 \
  --slippage-pct 0.0005
```

## Run with your CSV data

```bash
python3 user/run_custom_backtest.py \
  --asset AAPL \
  --csv /absolute/path/to/your_data.csv \
  --date-column date
```

If your date column is named differently:

```bash
python3 user/run_custom_backtest.py \
  --asset BTCUSD \
  --csv /absolute/path/to/btc_ohlcv.csv \
  --date-column timestamp
```

## CSV format requirements

The CSV must contain these columns (case-insensitive):

- `open`
- `high`
- `low`
- `close`
- `volume`

And optionally a date/time column (set with `--date-column`, default is `date`).

## Notes

- If `--csv` is provided, the script uses CSV mode.
- If `--csv` is not provided, it generates sample OHLCV data.
- The backtest engine requires at least 50 rows.
