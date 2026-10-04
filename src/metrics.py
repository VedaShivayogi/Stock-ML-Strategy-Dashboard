import numpy as np
import pandas as pd


def sharpe_ratio(returns, risk_free=0.0, periods=252):
    excess = returns - risk_free / periods
    if excess.std() == 0:
        return 0.0
    return np.sqrt(periods) * excess.mean() / excess.std()


def sortino_ratio(returns, risk_free=0.0, periods=252):
    excess = returns - risk_free / periods
    downside = excess[excess < 0].std()
    if downside == 0:
        return 0.0
    return np.sqrt(periods) * excess.mean() / downside


def max_drawdown(wealth_series):
    peak = wealth_series.cummax()
    drawdown = (wealth_series - peak) / peak
    return drawdown.min()


def calmar_ratio(returns, wealth_series, periods=252):
    ann_return = returns.mean() * periods
    mdd = abs(max_drawdown(wealth_series))
    if mdd == 0:
        return 0.0
    return ann_return / mdd


def hit_rate(actual, predicted):
    correct = (np.sign(predicted) == np.sign(actual)).mean()
    return correct


def profit_factor(strategy_returns):
    gains = strategy_returns[strategy_returns > 0].sum()
    losses = abs(strategy_returns[strategy_returns < 0].sum())
    if losses == 0:
        return np.inf
    return gains / losses


def apply_transaction_costs(positions, returns, cost=0.001):
    trades = np.diff(positions, prepend=0)
    costs = np.abs(trades) * cost
    return returns - costs


def full_report(val_df, pred_returns, buy_hold, ml_wealth, cost=0.001):
    close = val_df["Close"]
    actual_returns = close.pct_change().fillna(0)
    positions = np.sign(pred_returns)
    positions_shifted = np.zeros(len(positions))
    positions_shifted[1:] = positions[:-1]

    strategy_returns = pd.Series(
        positions_shifted * actual_returns.values,
        index=val_df.index
    )
    strategy_returns_net = pd.Series(
        apply_transaction_costs(positions_shifted, strategy_returns.values, cost),
        index=val_df.index
    )
    bh_returns = actual_returns

    print("\n  ── Financial Metrics ──────────────────────")
    for label, rets, wealth in [
        ("Buy & Hold ", bh_returns, buy_hold),
        ("ML (gross) ", strategy_returns, ml_wealth),
        ("ML (net)   ", strategy_returns_net, ml_wealth),
    ]:
        sr = sharpe_ratio(rets)
        so = sortino_ratio(rets)
        mdd = max_drawdown(wealth)
        cal = calmar_ratio(rets, wealth)
        pf = profit_factor(rets)
        print(f"  {label} | Sharpe: {sr:+.2f}  Sortino: {so:+.2f}  "
              f"MaxDD: {mdd:.1%}  Calmar: {cal:.2f}  ProfitFactor: {pf:.2f}")
    print(f"  Hit rate: {hit_rate(actual_returns.values[1:], pred_returns[:-1]):.1%}")
    print("  ───────────────────────────────────────────\n")
