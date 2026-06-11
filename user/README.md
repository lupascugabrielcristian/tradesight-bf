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

## Run a paper trade session (Alpaca paper account)

From project root:

```bash
python3 run_paper_trader.py
```

Useful commands:

```bash
python3 run_paper_trader.py --status
python3 run_paper_trader.py --report
```

## Where to change symbols, strategy, and time interval

### Symbols
Edit `src/trading/paper_trader.py` in `PaperTrader.__init__`, inside `self.config['trading_symbols']`.

### Strategy
TradeSight uses tournament winners first. If no winners are available, it uses fallback strategies in `scan_and_trade()` in `src/trading/paper_trader.py` (`winning_strategies` list). Keep only one entry there to force a single strategy.

### Time interval
There are two intervals:

- Signal candle timeframe (market data granularity): in `generate_trading_signals()` in `src/trading/paper_trader.py`, currently:
  - `timeframe='1Hour'` for primary signals
  - `timeframe='1Day'` for trend confirmation
- Scan frequency: `self.config['trade_frequency_hours']` in `PaperTrader.__init__` in `src/trading/paper_trader.py`.

### What run_paper_trader.py does?
  1. Starts session + websocket monitor for Alpaca trade updates  
     • src/trading/paper_trader.py:2053, src/trading/paper_trader.py:2019
  2. Syncs local state with Alpaca account/positions  
     • imports orphan positions, closes stale local ones  
     • src/trading/paper_trader.py:1796
  3. Runs one scan-and-trade pass  
     • premarket gap checks  
     • market regime detection  
     • stop-loss / take-profit / trailing-stop checks on open positions  
     • daily-loss circuit breaker  
     • picks strategies (recent tournament winners, or fallback list)  
     • loops symbols, generates signals, applies filters/guards, executes eligible orders  
     • src/trading/paper_trader.py:1483
  4. Closes aged positions (held too long)  
     • src/trading/paper_trader.py:1697
  5. Saves portfolio snapshot + generates a trading report file  
     • report saved to logs as trading_report_*.txt  
     • src/trading/paper_trader.py:2071
  6. Logs feedback metrics (if trades closed this session) for optimizer loop  
     • src/trading/paper_trader.py:2076
  7. Stops websocket monitor and returns report text  
     • src/trading/paper_trader.py:2131

  So it is not just “place one trade” — it’s a full risk-managed session pass: sync, risk checks, signal generation, potential order execution, and
  reporting.
