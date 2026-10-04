import numpy as np
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
import joblib


def build_models(cfg):
    rf = RandomForestRegressor(
        n_estimators=cfg["n_estimators"],
        max_depth=cfg["max_depth"],
        random_state=cfg["random_state"],
        n_jobs=-1,
    )
    xgb = XGBRegressor(
        n_estimators=cfg["n_estimators"],
        max_depth=cfg["max_depth"],
        random_state=cfg["random_state"],
        verbosity=0,
        n_jobs=-1,
    )
    lgbm = LGBMRegressor(
        n_estimators=cfg["n_estimators"],
        max_depth=cfg["max_depth"],
        random_state=cfg["random_state"],
        verbose=-1,
        n_jobs=-1,
    )
    ensemble = VotingRegressor(
        estimators=[("rf", rf), ("xgb", xgb), ("lgbm", lgbm)]
    )
    return {"random_forest": rf, "xgboost": xgb, "lightgbm": lgbm, "ensemble": ensemble}


def train_simple(model, X_train, y_train, X_val):
    model.fit(X_train, y_train)
    return model.predict(X_val)


def walk_forward_cv(model, X, y, n_splits=5):
    """
    Walk-forward (time-series aware) cross validation.
    Trains on past, validates on future — no lookahead bias.
    Returns mean direction accuracy across all folds.
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model.fit(X_tr, y_tr)
        preds = model.predict(X_val)
        acc = (np.sign(preds) == np.sign(y_val.values)).mean()
        scores.append(acc)
        print(f"    Fold {fold+1}: direction accuracy = {acc:.3f}")
    mean_acc = np.mean(scores)
    print(f"    Walk-forward mean accuracy: {mean_acc:.3f}")
    return scores, mean_acc


def save_model(model, path):
    joblib.dump(model, path)
    print(f"  Model saved to {path}")


def load_model(path):
    return joblib.load(path)
