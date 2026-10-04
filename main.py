import numpy as np
import pandas as pd
import yfinance as yf
import yaml

from src import build_features, FEATURE_COLS, build_models, train_simple, walk_forward_cv, save_model, full_report
from helper import (
    plot_results, animate_wealth_curves, wealth_curves,
    monte_carlo_wealth, monte_carlo_paths,
    plot_monte_carlo, animate_monte_carlo_paths,
)


def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def load_data(ticker, years, end_date):
    end = pd.Timestamp("today") if end_date == "today" else pd.Timestamp(end_date)
    start = end - pd.DateOffset(years=years)
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data


def split_data(df, feature_cols, train_ratio):
    n = int(len(df) * train_ratio)
    train, val = df.iloc[:n], df.iloc[n:]
    return (
        train[feature_cols], train["target"],
        val[feature_cols], val["target"],
    )


def run():
    cfg = load_config()
    dcfg = cfg["data"]
    mcfg = cfg["model"]
    bcfg = cfg["backtest"]
    mccfg = cfg["monte_carlo"]

    print(f"\nLoading {dcfg['ticker']} data...")
    raw = load_data(dcfg["ticker"], dcfg["years"], dcfg["end_date"])
    print(f"  {len(raw)} days  |  {raw.index[0].date()} → {raw.index[-1].date()}")

    print("Building features...")
    df = build_features(raw)
    X_train, y_train, X_val, y_val = split_data(df, FEATURE_COLS, mcfg["train_ratio"])
    train_size = len(X_train)
    print(f"  Train: {train_size}  Val: {len(X_val)}")

    print("\nWalk-forward cross-validation (Random Forest)...")
    models = build_models(mcfg)
    walk_forward_cv(models["random_forest"], df[FEATURE_COLS], df["target"], n_splits=5)

    print("\nTraining all models on full train set...")
    results = {}
    for name, model in models.items():
        preds = train_simple(model, X_train, y_train, X_val)
        acc = (np.sign(preds) == np.sign(y_val.values)).mean()
        results[name] = {"model": model, "preds": preds, "acc": acc}
        print(f"  {name:15s} direction accuracy: {acc:.1%}")

    best_name = max(results, key=lambda k: results[k]["acc"])
    best_preds = results[best_name]["preds"]
    print(f"\n  Best model: {best_name} ({results[best_name]['acc']:.1%})")

    save_model(results[best_name]["model"], f"{best_name}.pkl")

    print("\nComputing wealth curves...")
    val_df = df.iloc[train_size:]
    buy_hold, ml_wealth = wealth_curves(val_df, best_preds, bcfg["start_money"])

    print("Financial metrics...")
    full_report(val_df, best_preds, buy_hold, ml_wealth, bcfg["transaction_cost"])

    print("Plotting results...")
    plot_results(df, best_preds, train_size)

    print("Monte Carlo simulation...")
    val_returns = df.iloc[train_size:]["target"].values
    positions = np.sign(best_preds)
    ml_final, bh_final = monte_carlo_wealth(val_returns, positions, mccfg["n_sim"])
    print(f"  ML   median: ${np.median(ml_final):.0f}  |  5th–95th: ${np.percentile(ml_final,5):.0f}–${np.percentile(ml_final,95):.0f}")
    print(f"  B&H  median: ${np.median(bh_final):.0f}  |  5th–95th: ${np.percentile(bh_final,5):.0f}–${np.percentile(bh_final,95):.0f}")
    plot_monte_carlo(ml_final, bh_final, bcfg["start_money"])

    print("Animating wealth curves...")
    animate_wealth_curves(df, best_preds, train_size, frames=120, interval=50,
                          save_path="wealth_animation.gif")

    print("Animating Monte Carlo paths...")
    ml_paths, bh_paths = monte_carlo_paths(val_returns, positions, mccfg["n_paths"])
    animate_monte_carlo_paths(ml_paths, bh_paths, val_df.index,
                              save_path="monte_carlo_paths.gif")

    print("\nDone!")
    return results, df


if __name__ == "__main__":
    run()
