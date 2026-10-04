<<<<<<< HEAD
# Stock ML Strategy Dashboard

A machine learning project that tries to answer a deceptively simple question:
**can a model learn when to be in the market and when to step aside?**

Not to beat the market that's a high bar. But to survive it better. Take fewer hits during crashes, stay in during runs, and do it all without peeking at the future.

This started as a simple Random Forest script. It grew into a full interactive dashboard where you can type in any stock ticker, pick a model, and explore everything i.e.,: wealth curves, Monte Carlo simulation, SHAP explainability, and a day-by-day breakdown of every prediction the model made.

---

## Live dashboard

```bash
streamlit run dashboard/app.py
```

Type any ticker (SPY, AAPL, TSLA, QQQ...), hit **Run Pipeline**, and the whole analysis runs live.

The dashboard has three modes worth exploring:

**🎓 Beginner mode** — flip the toggle in the sidebar and every chart gets a plain-English explanation of what you're looking at and why it matters. Built so that anyone and not just ML people can follow along.

**⚖️ Compare mode** — run two tickers side by side. Same model, same time period, different stocks. Useful for seeing how the strategy behaves on a volatile stock (TSLA) vs a stable index (SPY).

**🔬 Day explainer** — pick any single trading day from a dropdown. A SHAP waterfall chart breaks down exactly why the model predicted up or down that day which signals pushed it higher, which pulled it lower. It's the closest thing to opening the black box.

---

## The results

On SPY (S&P 500 ETF), 10 years of data, 80/20 train/val split, data through April 2026:

|                     | Sharpe Ratio | Sortino | Max Drawdown | Hit Rate |
| ------------------- | ------------ | ------- | ------------ | -------- |
| Buy & Hold          | 1.21         | —       | -18.8%       | —        |
| ML Strategy (gross) | 1.00         | 1.53    | **-14.9%**   | 56%      |

The model didn't make more money. But it took a smaller hit during the April 2025 crash (-14.9% vs -18.8%). For a risk-adjusted strategy, surviving drawdowns matters as much as chasing returns.

The Monte Carlo simulation puts this in perspective — across 500 randomly shuffled return paths, the ML strategy's worst-case outcomes are consistently less severe than buy and hold.

---

## What's inside

```
stock-prediction/
├── src/
│   ├── features.py        # 19 technical indicators: MACD, Bollinger Bands, RSI, volatility
│   ├── models.py          # RF + XGBoost + LightGBM + Ensemble, walk-forward CV
│   ├── metrics.py         # Sharpe, Sortino, Calmar, max drawdown, profit factor
│   └── explainability.py  # SHAP — why did the model make that call?
├── dashboard/
│   └── app.py             # Streamlit app: live ticker, beginner mode, compare mode, day explainer
├── helper.py              # Wealth curves, Monte Carlo simulation, animated GIFs
├── main.py                # Full terminal pipeline: data → features → train → evaluate → plot
└── config.yaml            # All settings in one place: ticker, years, model params
```

---

## A few things worth calling out

**Walk-forward validation** — the train/test split isn't random. The model is always trained on the past and tested on the future, fold by fold. This is how it works in the real world, and it's the right way to evaluate a time-series strategy.

**Three models, one ensemble** — Random Forest, XGBoost, and LightGBM each make a prediction. The best single model is selected by direction accuracy on the validation set. The ensemble combines all three via soft voting.

**SHAP explainability** — after training, SHAP values show which features actually drove each prediction. On SPY, short-term momentum (MACD) and 10-day volatility dominate. The 50-day moving average, which most people assume is important, ranks near the bottom.

**Monte Carlo simulation** — instead of showing one wealth curve, the strategy is stress-tested across 500 randomly sampled return paths. The result is a distribution of outcomes, not just a single optimistic line.

**Transaction costs** — 0.1% per trade is applied throughout. Small, but it adds up over 500 validation days. The net Sharpe is the honest number.

**Always fresh data** — the end date is set to today automatically. Every run pulls the latest available data from Yahoo Finance.

---

## Setup

```bash
git clone https://github.com/your-username/stock-prediction.git
cd stock-prediction
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Interactive dashboard:**

```bash
streamlit run dashboard/app.py
```

**Full terminal pipeline + animated GIFs:**

```bash
python3 main.py
```

---

## Changing the ticker

Open `config.yaml`:

```yaml
data:
  ticker: "AAPL" # any Yahoo Finance ticker
  years: 10
```

Or just type it into the dashboard sidebar — no config editing needed.

---

## What I'd do next

- Hyperparameter tuning with Optuna, the scaffold is already in `src/models.py`
- LSTM layer to capture longer-range patterns the tree models miss
- Position sizing, Kelly criterion or fixed fractional instead of always going all in
- Deploy to Streamlit Community Cloud so anyone can use it without installing anything

---

## Tech stack

Python 3.11 · scikit-learn · XGBoost · LightGBM · SHAP · yfinance ·
pandas · numpy · Streamlit · Plotly · Matplotlib · PyYAML · joblib

---

_Built as a learning project to explore where ML and finance intersect and where they don't._

---

cd stock-prediction-main
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

streamlit run dashboard/app.py
=======
# Stock-ML-Strategy-Dashboard
>>>>>>> b13f44aa50a0704f34867721bb0efa148367303b
