#!/usr/bin/env python3
"""
compare_rf_models.py

Train and compare:
 - a simple from-scratch Random Forest (educational)
 - scikit-learn RandomForestRegressor (production)

Input: 'yield_dataset.csv' (one row per field-season, produced by your dataset builder)
Output: printed metrics, saved models: rf_scratch.pkl, rf_sklearn.joblib
"""

import time
import math
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import random
import sys

# -----------------------
# Utility metrics
# -----------------------
def rmse(y_true, y_pred):
    return math.sqrt(((y_true - y_pred) ** 2).mean())

# -----------------------
# Load dataset
# -----------------------
DATAFILE = "yield_dataset.csv"  # produced by your dataset builder
try:
    df = pd.read_csv(DATAFILE)
except FileNotFoundError:
    print(f"ERROR: {DATAFILE} not found. Generate dataset first and place it in this folder.")
    sys.exit(1)

# Drop rows with missing critical features or target
df = df.dropna(subset=['yield_kg_ha'])
# select features automatically (all numeric except lat/lon/year can be kept)
# If there are non-numeric columns, drop them or encode before use.
# We will pick a conservative set: numeric columns except target.
target_col = 'yield_kg_ha'
feature_cols = [c for c in df.columns if c != target_col and np.issubdtype(df[c].dtype, np.number)]

if len(feature_cols) == 0:
    raise ValueError("No numeric features detected. Edit the script to include proper features.")

X = df[feature_cols].values
y = df[target_col].values

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale numeric features for scikit model (optional but recommended)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------
# From-scratch Random Forest (simple, educational)
# - Binary regression trees using MSE split criterion
# - Random feature subset at each split (sqrt rule)
# - Bootstrap sampling per tree
# - Threshold candidates = percentiles to speed up
# WARNING: This implementation is not optimized; use small n_trees for speed.
# -----------------------
class ScratchTreeNode:
    __slots__ = ('pred', 'feat', 'thresh', 'left', 'right')
    def __init__(self, pred=None, feat=None, thresh=None, left=None, right=None):
        self.pred = pred
        self.feat = feat
        self.thresh = thresh
        self.left = left
        self.right = right

def mse_loss(y):
    if len(y) == 0:
        return 0.0
    return float(np.var(y) * len(y))

def best_split_quick(X, y, feature_indices, n_thresholds=10, min_samples_leaf=3):
    """
    For speed, evaluate thresholds at feature percentiles (n_thresholds).
    Returns (best_feat, best_thresh, best_score) or (None, None, None) if no split.
    """
    n, d = X.shape
    best_feat, best_thresh, best_score = None, None, float('inf')
    for feat in feature_indices:
        col = X[:, feat]
        # unique values check
        if np.all(col == col[0]):
            continue
        # candidate thresholds: percentiles
        percentiles = np.linspace(5, 95, n_thresholds)
        thresh_candidates = np.percentile(col, percentiles)
        for thresh in thresh_candidates:
            left_mask = col <= thresh
            right_mask = ~left_mask
            # ensure minimum samples in each leaf
            if left_mask.sum() < min_samples_leaf or right_mask.sum() < min_samples_leaf:
                continue
            score = mse_loss(y[left_mask]) + mse_loss(y[right_mask])
            if score < best_score:
                best_feat = feat
                best_thresh = float(thresh)
                best_score = float(score)
    if best_feat is None:
        return None, None, None
    return best_feat, best_thresh, best_score

def build_scratch_tree(X, y, depth=0, max_depth=6, min_samples_leaf=5):
    # stopping
    if depth >= max_depth or len(y) <= 2*min_samples_leaf or np.all(y == y[0]):
        return ScratchTreeNode(pred=float(np.mean(y)))
    m, d = X.shape
    # random subset of features (sqrt rule)
    k = max(1, int(math.sqrt(d)))
    features = np.random.choice(d, k, replace=False)
    feat, thresh, score = best_split_quick(X, y, features, n_thresholds=8, min_samples_leaf=min_samples_leaf)
    if feat is None:
        return ScratchTreeNode(pred=float(np.mean(y)))
    left_idx = X[:, feat] <= thresh
    right_idx = ~left_idx
    # recursive build
    left = build_scratch_tree(X[left_idx], y[left_idx], depth+1, max_depth, min_samples_leaf)
    right = build_scratch_tree(X[right_idx], y[right_idx], depth+1, max_depth, min_samples_leaf)
    return ScratchTreeNode(pred=None, feat=feat, thresh=thresh, left=left, right=right)

def predict_tree(node, x):
    while node.pred is None:
        if x[node.feat] <= node.thresh:
            node = node.left
        else:
            node = node.right
    return node.pred

class ScratchRandomForest:
    def __init__(self, n_trees=10, max_depth=6, min_samples_leaf=5, bootstrap=True, random_state=None):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.bootstrap = bootstrap
        self.trees = []
        self.random_state = random_state
        if random_state is not None:
            random.seed(random_state)
            np.random.seed(random_state)

    def fit(self, X, y):
        n = X.shape[0]
        self.trees = []
        for t in range(self.n_trees):
            if self.bootstrap:
                idx = np.random.choice(n, n, replace=True)
                Xb = X[idx]
                yb = y[idx]
            else:
                Xb = X
                yb = y
            tree = build_scratch_tree(Xb, yb, max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf)
            self.trees.append(tree)

    def predict(self, X):
        preds = np.zeros((len(self.trees), X.shape[0]), dtype=float)
        for i, tree in enumerate(self.trees):
            preds[i] = np.array([predict_tree(tree, x) for x in X])
        return preds.mean(axis=0)

# -----------------------
# Train Scratch RF
# -----------------------
print("=== Training scratch RF ===")
start_time = time.time()
scratch_rf = ScratchRandomForest(n_trees=12, max_depth=7, min_samples_leaf=5, random_state=42)
# We will train on UNscaled numeric features (X_train) to keep split thresholds interpretable
scratch_rf.fit(X_train, y_train)
t_scratch_train = time.time() - start_time
print(f"Scratch RF training time: {t_scratch_train:.2f}s")

# Predict and evaluate
start_time = time.time()
y_pred_scratch = scratch_rf.predict(X_test)
t_scratch_pred = time.time() - start_time
print(f"Scratch RF predict time: {t_scratch_pred:.2f}s")
rmse_scratch = rmse(y_test, y_pred_scratch)
r2_scratch = r2_score(y_test, y_pred_scratch)
print(f"Scratch RF  -> RMSE: {rmse_scratch:.2f}, R2: {r2_scratch:.3f}")

# Save scratch model
with open("rf_scratch.pkl", "wb") as f:
    pickle.dump(scratch_rf, f)

# -----------------------
# scikit-learn Random Forest (production)
# -----------------------
print("\n=== Training scikit-learn RandomForestRegressor ===")
start_time = time.time()
rf_sklearn = RandomForestRegressor(n_estimators=200, max_depth=20, n_jobs=-1, random_state=42)
rf_sklearn.fit(X_train_scaled, y_train)
t_sklearn_train = time.time() - start_time
print(f"sklearn RF training time: {t_sklearn_train:.2f}s")

# Predict and evaluate
start_time = time.time()
y_pred_sklearn = rf_sklearn.predict(X_test_scaled)
t_sklearn_pred = time.time() - start_time
rmse_sklearn = rmse(y_test, y_pred_sklearn)
r2_sklearn = r2_score(y_test, y_pred_sklearn)
print(f"sklearn RF predict time: {t_sklearn_pred:.2f}s")
print(f"sklearn RF -> RMSE: {rmse_sklearn:.2f}, R2: {r2_sklearn:.3f}")

# Save sklearn model + scaler
joblib.dump({'model': rf_sklearn, 'scaler': scaler, 'features': feature_cols}, "rf_sklearn.joblib")

# -----------------------
# Simple comparison & notes
# -----------------------
print("\n=== Comparison ===")
print(f"Scratch RMSE: {rmse_scratch:.2f}, R2: {r2_scratch:.3f}, train_time: {t_scratch_train:.2f}s")
print(f"sklearn  RMSE: {rmse_sklearn:.2f}, R2: {r2_sklearn:.3f}, train_time: {t_sklearn_train:.2f}s")
print("\nNotes:")
print("- scikit-learn model is usually faster (C-optimized) and more accurate; use it for production/demo.")
print("- scratch model helps illustrate RF internals (bootstrapping, feature subsampling, splitting).")
print("- If the scratch model is much worse, increase n_trees and/or max_depth, but runtime will rise.")
print("- You can compute feature importances from sklearn via rf_sklearn.feature_importances_")

# Print top-8 feature importances (sklearn)
feat_imp = rf_sklearn.feature_importances_
imp_df = pd.DataFrame({'feature': feature_cols, 'importance': feat_imp}).sort_values('importance', ascending=False)
print("\nTop features (sklearn RF):")
print(imp_df.head(8).to_string(index=False))

# Quick permutation importance (cheap, single pass) for top 5 features (optional)
try:
    from sklearn.inspection import permutation_importance
    print("\nComputing permutation importance (this may take a few seconds)...")
    perm = permutation_importance(rf_sklearn, X_test_scaled, y_test, n_repeats=10, random_state=42, n_jobs=1)
    perm_imp = pd.DataFrame({'feature': feature_cols, 'perm_importance': perm.importances_mean}).sort_values('perm_importance', ascending=False)
    print(perm_imp.head(8).to_string(index=False))
except Exception as e:
    print("Permutation importance skipped (error):", e)

print("\nDone. Models saved: rf_scratch.pkl, rf_sklearn.joblib")
