import numpy as np
import pandas as pd
import shap
import matplotlib.pyplot as plt


def get_shap_explainer(model, X_train):
    explainer = shap.TreeExplainer(model)
    return explainer


def shap_summary(explainer, X_val, max_display=15, save_path=None):
    shap_values = explainer(X_val)
    fig, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(
        shap_values, X_val,
        max_display=max_display,
        show=False
    )
    plt.title("SHAP Feature Importance — what drives each prediction")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved SHAP summary to {save_path}")
    plt.show()
    return shap_values


def shap_waterfall(explainer, X_val, day_index=0, save_path=None):
    shap_values = explainer(X_val)
    fig, ax = plt.subplots(figsize=(10, 5))
    shap.waterfall_plot(shap_values[day_index], show=False)
    plt.title(f"SHAP Waterfall — why the model predicted this on day {day_index}")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved SHAP waterfall to {save_path}")
    plt.show()
    return shap_values


def shap_feature_importance(explainer, X_val):
    shap_values = explainer(X_val)
    vals = np.abs(shap_values.values).mean(axis=0)
    importance_df = pd.DataFrame({
        "feature": X_val.columns,
        "mean_abs_shap": vals
    }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
    return importance_df
