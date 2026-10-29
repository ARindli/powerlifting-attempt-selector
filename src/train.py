"""Trener og sammenligner modellene. Kjøres med: python src/train.py"""
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEED = 42
FIG = "rapport/figurer"

# Data og features
df = pd.read_parquet("data/processed/attempts.parquet")

NUMERIC = ["attempt", "sex", "age", "bw", "tested", "wraps", "weight", "weight_bw", "pct_pr",
           "jump_kg", "jump_pct", "prev_missed", "misses_this_lift", "misses_prior_lifts",
           "n_prev_meets", "hist_rate", "days_since_last"]
CATEGORICAL = ["lift"]                     # 0 = knebøy, 1 = benk, 2 = markløft
FEATURES = NUMERIC + CATEGORICAL
TARGET = "made"

# Domenekunnskap: tyngre vekt (eller større hopp) skal aldri gi høyere sjanse, alt annet likt.
# -1 betyr at sannsynligheten bare kan synke når featuren øker.
MONOTONE = {"weight": -1, "weight_bw": -1, "pct_pr": -1, "jump_kg": -1, "jump_pct": -1}

# Tidsbasert split: tren på fortiden, test på fremtiden
# (en tilfeldig split ville blandet forsøk fra samme stevne i train og test)
train = df[df.year <= 2022].sample(1_000_000, random_state=SEED)   # utvalg for å spare tid
val = df[df.year == 2023].sample(300_000, random_state=SEED)
test = df[df.year >= 2024]
print(f"train {len(train):,} | val {len(val):,} | test {len(test):,}")
assert set(train.year) & set(test.year) == set()   # ingen overlapp i tid

X_train, y_train = train[FEATURES], train[TARGET]
X_val, y_val = val[FEATURES], val[TARGET]
X_test, y_test = test[FEATURES], test[TARGET]


def scores(y, p):
    return {"ROC AUC": roc_auc_score(y, p), "Log loss": log_loss(y, p), "Brier": brier_score_loss(y, p)}


# Baseline uten ML: godkjentrate per løft og forsøksnummer
rate = train.groupby(["lift", "attempt"])[TARGET].mean()
baseline = lambda d: rate.loc[list(zip(d.lift, d.attempt))].to_numpy()

# Modell 1: Logistisk regresjon i en pipeline
# Manglende verdier fylles med median, tallene skaleres, løft one-hot-kodes.
# Pipelinen tilpasses kun på treningsdata, så ingen lekkasje fra val/test.
preprocess = ColumnTransformer([
    ("num", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                      ("scale", StandardScaler())]), NUMERIC),
    ("cat", OneHotEncoder(), CATEGORICAL),
])
logreg = Pipeline([("prep", preprocess), ("model", LogisticRegression(max_iter=1000))])
logreg.fit(X_train, y_train)

# Modell 2: Gradient boosting (trær). Håndterer manglende verdier selv
# og trenger ikke skalering.
gb = HistGradientBoostingClassifier(categorical_features=["lift"], monotonic_cst=MONOTONE,
                                    random_state=SEED)
gb.fit(X_train, y_train)

# Sammenlign på valideringssettet (testsettet røres ikke ennå)
val_results = pd.DataFrame({
    "Baseline (løft × forsøk)": scores(y_val, baseline(X_val)),
    "Logistisk regresjon": scores(y_val, logreg.predict_proba(X_val)[:, 1]),
    "Gradient boosting": scores(y_val, gb.predict_proba(X_val)[:, 1]),
}).T
print("\nValidering (2023):\n", val_results.round(4))

# Hyperparametersøk på beste modell (gradient boosting) med kryssvalidering
search = RandomizedSearchCV(
    HistGradientBoostingClassifier(categorical_features=["lift"], monotonic_cst=MONOTONE,
                                   random_state=SEED),
    param_distributions={
        "learning_rate": [0.03, 0.05, 0.1, 0.2],
        "max_leaf_nodes": [15, 31, 63, 127],
        "min_samples_leaf": [20, 100, 500],
        "max_iter": [200, 400],
    },
    n_iter=10, cv=3, scoring="neg_log_loss", random_state=SEED, n_jobs=-1,
)
search.fit(X_train.iloc[:300_000], y_train.iloc[:300_000])   # mindre utvalg for å spare tid
print("\nBeste hyperparametre:", search.best_params_)

gb_tuned = HistGradientBoostingClassifier(categorical_features=["lift"], monotonic_cst=MONOTONE,
                                          random_state=SEED, **search.best_params_)
gb_tuned.fit(X_train, y_train)
print("Val etter tuning:", {k: round(v, 4) for k, v in
                            scores(y_val, gb_tuned.predict_proba(X_val)[:, 1]).items()})

# Endelig evaluering på testsettet (2024+), én gang
p_test = {
    "Baseline (løft × forsøk)": baseline(X_test),
    "Logistisk regresjon": logreg.predict_proba(X_test)[:, 1],
    "Gradient boosting (tunet)": gb_tuned.predict_proba(X_test)[:, 1],
}
test_results = pd.DataFrame({name: scores(y_test, p) for name, p in p_test.items()}).T
print("\nTest (2024+):\n", test_results.round(4))
test_results.round(4).to_csv("rapport/resultater.csv")

# Figurer til rapporten
# Kalibrering: når modellen sier 70 %, blir 70 % godkjent?
fig, ax = plt.subplots(figsize=(5, 5))
ax.plot([0, 1], [0, 1], "k--", label="Perfekt kalibrert")
for name in ["Logistisk regresjon", "Gradient boosting (tunet)"]:
    obs, pred = calibration_curve(y_test, p_test[name], n_bins=10)
    ax.plot(pred, obs, marker="o", label=name)
ax.set(xlabel="Predikert sannsynlighet", ylabel="Faktisk andel godkjent", title="Kalibrering (test)")
ax.legend(); fig.tight_layout(); fig.savefig(f"{FIG}/kalibrering.png", dpi=120)

# ROC-kurver
fig, ax = plt.subplots(figsize=(5, 5))
for name, p in p_test.items():
    RocCurveDisplay.from_predictions(y_test, p, name=name, ax=ax)
ax.set_title("ROC-kurve (test)"); fig.tight_layout(); fig.savefig(f"{FIG}/roc.png", dpi=120)

# Feature importance: hvor mye dårligere blir modellen når en feature stokkes?
sample = test.sample(50_000, random_state=SEED)
imp = permutation_importance(gb_tuned, sample[FEATURES], sample[TARGET], scoring="neg_log_loss",
                             n_repeats=3, random_state=SEED, n_jobs=-1)
importance = pd.Series(imp.importances_mean, index=FEATURES).sort_values()
fig, ax = plt.subplots(figsize=(6, 5))
importance.plot.barh(ax=ax)
ax.set(xlabel="Økning i log loss når featuren stokkes", title="Feature importance (test)")
fig.tight_layout(); fig.savefig(f"{FIG}/feature_importance.png", dpi=120)
print("\nViktigste features:\n", importance.sort_values(ascending=False).head(8).round(4))

# Lagre modellen som nettsiden skal bruke
joblib.dump({"model": gb_tuned, "features": FEATURES}, "models/model.joblib")
print("\nLagret models/model.joblib")