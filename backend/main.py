#import the lib.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import yfinance as yf
from cachetools import cached, TTLCache

from src.features import build_features, FEATURE_COLS
from src.models import build_models, train_simple
from src.metrics import sharpe_ratio, sortino_ratio, max_drawdown, hit_rate
from src.explainability import get_shap_explainer, shap_feature_importance
from helper import wealth_curves, monte_carlo_wealth, monte_carlo_paths

app = FastAPI(title="Stock ML API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = TTLCache(maxsize=100, ttl=3600)

@cached(cache)
def get_raw_data(ticker, years):
    end = pd.Timestamp("today")
    start = end - pd.DateOffset(years=years)
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    return raw

@cached(cache)
def run_pipeline(ticker, years, train_ratio, model_choice, start_money):
    raw = get_raw_data(ticker, years)
    if raw.empty:
        raise ValueError(f"No data found for {ticker}")
    df = build_features(raw)
    n = int(len(df) * train_ratio)
    train_df, val_df = df.iloc[:n], df.iloc[n:]
    X_train, y_train = train_df[FEATURE_COLS], train_df["target"]
    X_val, y_val = val_df[FEATURE_COLS], val_df["target"]
    cfg = {"n_estimators": 100, "max_depth": 8, "random_state": 42}
    models = build_models(cfg)
    model = models[model_choice]
    preds = train_simple(model, X_train, y_train, X_val)
    bh, ml = wealth_curves(val_df, preds, start_money)
    close = val_df["Close"]
    actual = close.pct_change().fillna(0)
    pos = np.sign(preds)
    pos_sh = np.zeros(len(pos)); pos_sh[1:] = pos[:-1]
    strat = pd.Series(pos_sh * actual.values, index=val_df.index)
    return {
        "df": df, "val_df": val_df, "X_train": X_train, "y_train": y_train,
        "X_val": X_val, "y_val": y_val, "preds": preds, "buy_hold": bh,
        "ml_wealth": ml, "actual_returns": actual, "strategy_returns": strat,
        "positions": pos, "model": model, "close": close, "n": n
    }

@app.get("/api/run")
def api_run(
    ticker: str = Query("SPY"), 
    years: int = Query(10), 
    train_ratio: float = Query(0.8), 
    model: str = Query("random_forest"), 
    start_money: float = Query(100.0)
):
    try:
        r = run_pipeline(ticker, years, train_ratio, model, start_money)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    dates = r["val_df"].index.strftime("%Y-%m-%d").tolist()
    
    metrics = {
        "sharpe_bh": float(sharpe_ratio(r["actual_returns"])),
        "sharpe_ml": float(sharpe_ratio(r["strategy_returns"])),
        "maxdd_bh": float(max_drawdown(r["buy_hold"])),
        "maxdd_ml": float(max_drawdown(r["ml_wealth"])),
        "hit_rate": float(hit_rate(r["y_val"].values, r["preds"])),
        "sortino_ml": float(sortino_ratio(r["strategy_returns"]))
    }
    
    return {
        "dates": dates,
        "metrics": metrics,
        "buy_hold": r["buy_hold"].tolist(),
        "ml_wealth": r["ml_wealth"].tolist(),
        "close": r["close"].tolist(),
        "preds": r["preds"].tolist(),
        "positions": r["positions"].tolist(),
        "actual_returns": r["actual_returns"].tolist()
    }

@app.get("/api/montecarlo")
def api_montecarlo(
    ticker: str = Query("SPY"), 
    years: int = Query(10), 
    train_ratio: float = Query(0.8), 
    model: str = Query("random_forest"), 
    start_money: float = Query(100.0)
):
    try:
        r = run_pipeline(ticker, years, train_ratio, model, start_money)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    val_ret = r["df"].iloc[r["n"]:]["target"].values
    ml_f, bh_f = monte_carlo_wealth(val_ret, r["positions"], n_sim=500, start_money=start_money)
    
    return {
        "ml_final": ml_f.tolist(),
        "bh_final": bh_f.tolist(),
        "ml_p5": float(np.percentile(ml_f, 5)),
        "ml_p50": float(np.percentile(ml_f, 50)),
        "ml_p95": float(np.percentile(ml_f, 95)),
        "bh_p5": float(np.percentile(bh_f, 5)),
        "bh_p50": float(np.percentile(bh_f, 50)),
        "bh_p95": float(np.percentile(bh_f, 95))
    }

@app.get("/api/shap/importance")
def api_shap_importance(
    ticker: str = Query("SPY"), 
    years: int = Query(10), 
    train_ratio: float = Query(0.8), 
    model: str = Query("random_forest"), 
    start_money: float = Query(100.0)
):
    if model == "ensemble":
        raise HTTPException(status_code=400, detail="SHAP not supported for ensemble model")
        
    try:
        r = run_pipeline(ticker, years, train_ratio, model, start_money)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    explainer = get_shap_explainer(r["model"], r["X_train"])
    imp_df = shap_feature_importance(explainer, r["X_val"])
    
    return imp_df.to_dict(orient="records")

@app.get("/api/shap/day")
def api_shap_day(
    ticker: str = Query("SPY"), 
    date: str = Query(...),
    years: int = Query(10), 
    train_ratio: float = Query(0.8), 
    model: str = Query("random_forest"), 
    start_money: float = Query(100.0)
):
    if model == "ensemble":
        raise HTTPException(status_code=400, detail="SHAP not supported for ensemble model")
        
    try:
        r = run_pipeline(ticker, years, train_ratio, model, start_money)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    dates = r["val_df"].index.strftime("%Y-%m-%d").tolist()
    if date not in dates:
        raise HTTPException(status_code=404, detail="Date not found in validation set")
        
    day_i = dates.index(date)
    explainer = get_shap_explainer(r["model"], r["X_train"])
    shap_values = explainer(r["X_val"])
    
    sv = shap_values[day_i]
    
    return {
        "date": date,
        "base_value": float(sv.base_values),
        "values": sv.values.tolist(),
        "feature_names": r["X_val"].columns.tolist(),
        "prediction": float(r["preds"][day_i]),
        "actual": float(r["y_val"].values[day_i])
    }

@app.get("/api/watchlist")
def api_watchlist(tickers: str = Query("AAPL,MSFT,SPY")):
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    results = []
    
    for t in ticker_list:
        try:
            raw = get_raw_data(t, 2)
            if raw.empty:
                continue
            
            close = raw["Close"]
            last_price = close.iloc[-1]
            if len(close) > 1:
                prev_price = close.iloc[-2]
                pct_change = (last_price - prev_price) / prev_price
            else:
                pct_change = 0.0
            sparkline = close.tail(7).tolist()
            
            try:
                r = run_pipeline(t, 2, 0.8, "random_forest", 100.0)
                signal = "LONG" if r["preds"][-1] > 0 else "SHORT"
            except Exception:
                signal = "NEUTRAL"
                
            results.append({
                "ticker": t,
                "price": float(last_price),
                "change": float(pct_change),
                "sparkline": sparkline,
                "signal": signal,
                "name": t
            })
        except Exception:
            continue
            
    return results
