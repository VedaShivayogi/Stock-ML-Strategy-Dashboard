import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import yfinance as yf
import shap

from src.features import build_features, FEATURE_COLS
from src.models import build_models, train_simple
from src.metrics import sharpe_ratio, sortino_ratio, max_drawdown, hit_rate
from src.explainability import get_shap_explainer, shap_feature_importance
from helper import wealth_curves, monte_carlo_wealth, monte_carlo_paths

st.set_page_config(page_title="Stock ML Dashboard", layout="wide")

st.markdown("""
<style>
  .explain-box {
    background: #f0f7ff;
    border-left: 4px solid #3b82f6;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: #1e3a5f;
  }
  .stMetric { background: #f8f9fa; border-radius: 8px; padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def explain(text):
    st.info("💡 " + text)

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("Configuration")

beginner_mode = st.sidebar.toggle("Beginner mode", value=False,
    help="Turns on plain-English explanations for every section")

compare_mode = st.sidebar.toggle("Compare two tickers", value=False)

st.sidebar.divider()
ticker1 = st.sidebar.text_input("Ticker" if not compare_mode else "Ticker 1", value="SPY").upper()
ticker2 = ""
if compare_mode:
    ticker2 = st.sidebar.text_input("Ticker 2", value="AAPL").upper()

years        = st.sidebar.slider("Years of data", 2, 15, 10)
train_ratio  = st.sidebar.slider("Train ratio", 0.6, 0.9, 0.8)
model_choice = st.sidebar.selectbox("Model", ["random_forest","xgboost","lightgbm","ensemble"])
start_money  = st.sidebar.number_input("Starting money ($)", value=100, step=10)
trans_cost   = st.sidebar.number_input("Transaction cost", value=0.001, step=0.0005, format="%.4f")
run_btn      = st.sidebar.button("Run Pipeline", use_container_width=True)

st.title("Stock ML Strategy Dashboard")
st.caption("Random Forest · XGBoost · LightGBM · Monte Carlo · SHAP Explainability")

if beginner_mode:
    explain("""Welcome! This dashboard trains a machine learning model on historical stock prices,
    then tests whether its trading strategy would have made money compared to simply buying and holding.
    Use the sidebar to pick any stock ticker, adjust settings, and hit Run Pipeline.""")

if not run_btn:
    if "results" not in st.session_state:
        st.info("👈 Configure your settings in the sidebar and click **Run Pipeline** to start.")
        st.stop()
    else:
        results = st.session_state["results"]

# ── Pipeline function ─────────────────────────────────────
@st.cache_data(show_spinner=False)
def run_pipeline(ticker, years, train_ratio, model_choice, start_money, trans_cost):
    end = pd.Timestamp("today")
    start = end - pd.DateOffset(years=years)
    raw   = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    if raw.empty:
        return None
    df = build_features(raw)
    n  = int(len(df) * train_ratio)
    train_df, val_df = df.iloc[:n], df.iloc[n:]
    X_train, y_train = train_df[FEATURE_COLS], train_df["target"]
    X_val,   y_val   = val_df[FEATURE_COLS],   val_df["target"]
    cfg    = {"n_estimators":100, "max_depth":8, "random_state":42}
    models = build_models(cfg)
    preds  = train_simple(models[model_choice], X_train, y_train, X_val)
    bh, ml = wealth_curves(val_df, preds, start_money)
    close  = val_df["Close"]
    actual = close.pct_change().fillna(0)
    pos    = np.sign(preds)
    pos_sh = np.zeros(len(pos)); pos_sh[1:] = pos[:-1]
    strat  = pd.Series(pos_sh * actual.values, index=val_df.index)
    return dict(df=df, val_df=val_df, X_train=X_train, y_train=y_train,
                X_val=X_val, y_val=y_val, preds=preds, buy_hold=bh,
                ml_wealth=ml, actual_returns=actual, strategy_returns=strat,
                positions=pos, model=models[model_choice], close=close, n=n)

# ── Run ───────────────────────────────────────────────────
tickers_to_run = [ticker1] + ([ticker2] if compare_mode and ticker2 else [])
results = {}
for t in tickers_to_run:
    with st.spinner(f"Running pipeline for {t}..."):
        r = run_pipeline(t, years, train_ratio, model_choice, start_money, trans_cost)
    if r is None:
        st.error(f"No data found for {t}.")
        st.stop()
    results[t] = r
    st.success(f"{t} · {len(r['df'])} days · Train: {r['n']} · Val: {len(r['val_df'])}")

# ══════════════════════════════════════════════════════════
# SECTION 1 — PERFORMANCE METRICS
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Performance Metrics")

if beginner_mode:
    explain("""These numbers summarise how well each strategy performed.
    **Sharpe ratio** — how much return you got per unit of risk (higher = better).
    **Max Drawdown** — the worst loss from a peak (e.g. -18% means you lost 18% at the worst point before recovering).
    **Hit Rate** — % of days the model correctly predicted which direction the price moved.
    **Sortino** — like Sharpe but only penalises *downside* volatility, not upside swings.""")

for t, r in results.items():
    if compare_mode:
        st.markdown(f"#### {t}")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Sharpe (B&H)",      f"{sharpe_ratio(r['actual_returns']):.2f}")
    c2.metric("Sharpe (ML)",       f"{sharpe_ratio(r['strategy_returns']):.2f}")
    c3.metric("MaxDD (B&H)",       f"{max_drawdown(r['buy_hold']):.1%}")
    c4.metric("MaxDD (ML)",        f"{max_drawdown(r['ml_wealth']):.1%}")
    c5.metric("Hit Rate",          f"{hit_rate(r['y_val'].values, r['preds']):.1%}")
    c6.metric("Sortino (ML)",      f"{sortino_ratio(r['strategy_returns']):.2f}")

# ══════════════════════════════════════════════════════════
# SECTION 2 — WEALTH CURVES
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Wealth Curves")

if beginner_mode:
    explain("""Imagine you started with $100 on the first day of the test period.
    The **green line** shows what happened if you just bought and held.
    The **purple line** shows what happened if you followed the ML model's buy/sell signals.
    Closer together = similar performance. The interesting part is what happens during crashes.""")

if compare_mode:
    fig = go.Figure()
    colours = {"buy_hold": ["#16a34a","#15803d"], "ml": ["#7c3aed","#4f46e5"]}
    for i, (t, r) in enumerate(results.items()):
        fig.add_trace(go.Scatter(x=r['val_df'].index, y=r['buy_hold'],
            name=f"{t} Buy & Hold", line=dict(color=colours["buy_hold"][i], width=2)))
        fig.add_trace(go.Scatter(x=r['val_df'].index, y=r['ml_wealth'],
            name=f"{t} ML", line=dict(color=colours["ml"][i], width=2, dash="dot")))
else:
    r = results[ticker1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r['val_df'].index, y=r['buy_hold'],
        name="Buy & Hold", line=dict(color="#16a34a", width=2)))
    fig.add_trace(go.Scatter(x=r['val_df'].index, y=r['ml_wealth'],
        name=f"ML ({model_choice})", line=dict(color="#7c3aed", width=2)))

fig.add_hline(y=start_money, line_dash="dash", line_color="gray", opacity=0.4)
fig.update_layout(xaxis_title="Date", yaxis_title="Wealth ($)",
    hovermode="x unified", height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# SECTION 3 — PRICE PREDICTION
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Actual vs Predicted Price")

if beginner_mode:
    explain("""The model doesn't predict an exact price it predicts whether tomorrow will be
    *higher or lower* than today. This chart shows what the predicted next-day price would look like
    if you applied that prediction to today's actual price. When the lines track closely,
    the model is reading the direction well.""")

cols = st.columns(len(results))
for col, (t, r) in zip(cols, results.items()):
    with col:
        pred_price = r['close'] * (1 + r['preds'])
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=r['val_df'].index, y=r['close'].squeeze(),
            name="Actual", line=dict(color="#2563eb", width=2)))
        fig2.add_trace(go.Scatter(x=r['val_df'].index, y=pred_price.squeeze(),
            name="Predicted", line=dict(color="#f97316", width=1.5, dash="dash")))
        fig2.update_layout(title=t, xaxis_title="Date", yaxis_title="Price ($)",
            hovermode="x unified", height=350,
            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════
# SECTION 4 — MONTE CARLO
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Monte Carlo Simulation")

if beginner_mode:
    explain("""The single wealth curve above shows *one* possible outcome the actual sequence of
    market returns. But what if the returns had come in a different order?
    Monte Carlo runs 500 simulations by randomly shuffling the historical returns.
    The result is a *range* of possible outcomes, not just one line.
    A tight fan = more predictable. A wide fan = more uncertainty.""")

for t, r in results.items():
    if compare_mode:
        st.markdown(f"#### {t}")
    with st.spinner(f"Running Monte Carlo for {t}..."):
        val_ret  = r['df'].iloc[r['n']:]["target"].values
        ml_f, bh_f = monte_carlo_wealth(val_ret, r['positions'], n_sim=500)
        ml_p, bh_p = monte_carlo_paths(val_ret, r['positions'], n_sim=100)

    mc1, mc2 = st.columns(2)
    with mc1:
        fmc = go.Figure()
        fmc.add_trace(go.Histogram(x=bh_f, name="Buy & Hold",
            opacity=0.6, marker_color="#16a34a", nbinsx=40))
        fmc.add_trace(go.Histogram(x=ml_f, name="ML strategy",
            opacity=0.6, marker_color="#7c3aed", nbinsx=40))
        fmc.add_vline(x=start_money, line_dash="dash", line_color="gray")
        fmc.update_layout(barmode="overlay", title="Final wealth distribution",
            xaxis_title="Final wealth ($)", height=320)
        st.plotly_chart(fmc, use_container_width=True)

    with mc2:
        fb = go.Figure()
        fb.add_trace(go.Box(y=bh_f, name="Buy & Hold",
            marker_color="#16a34a", boxmean=True))
        fb.add_trace(go.Box(y=ml_f, name="ML strategy",
            marker_color="#7c3aed", boxmean=True))
        fb.add_hline(y=start_money, line_dash="dash", line_color="gray")
        fb.update_layout(title="Spread of outcomes", height=320)
        st.plotly_chart(fb, use_container_width=True)

    p5m,p50m,p95m = np.percentile(ml_f,[5,50,95])
    p5b,p50b,p95b = np.percentile(bh_f,[5,50,95])
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("ML Median",      f"${p50m:.0f}")
    c2.metric("ML 5th–95th",    f"${p5m:.0f} – ${p95m:.0f}")
    c3.metric("B&H Median",     f"${p50b:.0f}")
    c4.metric("B&H 5th–95th",   f"${p5b:.0f} – ${p95b:.0f}")

# ══════════════════════════════════════════════════════════
# SECTION 5 — SHAP FEATURE IMPORTANCE
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("SHAP Feature Importance")

if beginner_mode:
    explain("""The model looks at 19 different signals before making each prediction.
    SHAP (SHapley Additive exPlanations) measures how much each signal *actually influenced*
    the model's decision not just whether it was correlated with the outcome.
    Longer bar = bigger influence. This is one of the most important tools in modern ML
    for understanding *why* a model does what it does.""")

for t, r in results.items():
    if compare_mode:
        st.markdown(f"#### {t}")
    if model_choice != "ensemble":
        with st.spinner(f"Computing SHAP values for {t}..."):
            explainer   = get_shap_explainer(r['model'], r['X_train'])
            imp_df      = shap_feature_importance(explainer, r['X_val'])
        fig_shap = px.bar(imp_df, x="mean_abs_shap", y="feature",
            orientation="h", color="mean_abs_shap",
            color_continuous_scale="Purples",
            title=f"Feature importance — {t}")
        fig_shap.update_layout(yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False, height=480,
            xaxis_title="Mean |SHAP| value", yaxis_title="")
        st.plotly_chart(fig_shap, use_container_width=True)
    else:
        st.info("Switch to a single model (not ensemble) to see SHAP values.")

# ══════════════════════════════════════════════════════════
# SECTION 6 — SHAP WATERFALL (single day explainer)
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Why did the model predict this day?")

if beginner_mode:
    explain("""Pick any trading day from the validation period.
    The waterfall chart breaks down *exactly* why the model predicted up or down that day 
    which signals pushed the prediction higher (red) and which pulled it lower (blue).
    It's like opening the black box and seeing the reasoning step by step.""")

if model_choice != "ensemble":
    r      = results[ticker1]
    dates  = r['val_df'].index.strftime("%Y-%m-%d").tolist()
    chosen = st.selectbox("Pick a trading day to explain:", dates, index=len(dates)//2)
    day_i  = dates.index(chosen)

    pred_dir = "UP" if r['preds'][day_i] > 0 else "DOWN"
    actual_dir = " UP" if r['y_val'].values[day_i] > 0 else "DOWN"
    w1, w2, w3 = st.columns(3)
    w1.metric("Date", chosen)
    w2.metric("Model predicted", pred_dir)
    w3.metric("What actually happened", actual_dir,
        delta="Correct" if pred_dir == actual_dir else "Wrong",
        delta_color="normal" if pred_dir == actual_dir else "inverse")

    with st.spinner("Building waterfall explanation..."):
        explainer   = get_shap_explainer(r['model'], r['X_train'])
        shap_values = explainer(r['X_val'])

    fig_wf, ax = plt.subplots(figsize=(10, 5))
    shap.waterfall_plot(shap_values[day_i], show=False, max_display=15)
    plt.title(f"Why the model said {pred_dir} on {chosen}", fontsize=13)
    plt.tight_layout()
    st.pyplot(fig_wf)
    plt.close()

    if beginner_mode:
        explain("""Red bars pushed the prediction toward UP. Blue bars pushed it toward DOWN.
        The bar length = how much that feature influenced this specific prediction.
        E(f(x)) is the average prediction across all days think of it as the starting point
        before any features are applied.""")
else:
    st.info("Switch to a single model to use the day explainer.")

# ══════════════════════════════════════════════════════════
# SECTION 7 — DAILY POSITIONS TABLE
# ══════════════════════════════════════════════════════════
st.divider()
st.subheader("Recent Daily Positions")

if beginner_mode:
    explain("""This table shows the model's last 30 calls.
    **LONG** means it predicted the price would go up , so it invested.
    **SHORT** means it predicted the price would go down ,  so it bet against it.
    Compare the predicted return vs actual return to see where it got it right and wrong.""")

r = results[ticker1]
pos_df = pd.DataFrame({
    "Date":             r['val_df'].index,
    "Close ($)":        r['close'].squeeze().values,
    "Predicted Return": r['preds'],
    "Position":         ["LONG" if p > 0 else "SHORT" for p in r['preds']],
    "Actual Return":    r['actual_returns'].values,
    "Correct?":         ["✅" if np.sign(p)==np.sign(a) else "❌"
                         for p,a in zip(r['preds'], r['actual_returns'].values)]
}).set_index("Date")

st.dataframe(
    pos_df.tail(30).style.format({
        "Close ($)":        "${:.2f}",
        "Predicted Return": "{:.4f}",
        "Actual Return":    "{:.4f}",
    }),
    use_container_width=True
)
st.caption("Showing last 30 trading days.")
