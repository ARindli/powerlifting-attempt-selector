"""Lager treningssettet, én rad per forsøk. Kjøres med: python src/prepare_data.py"""
import glob

import numpy as np
import pandas as pd

OUT = "data/processed/attempts.parquet"
LIFTS = ["Squat", "Bench", "Deadlift"]

# Les inn bare kolonnene vi trenger
csv = glob.glob("data/raw/openpowerlifting-*/openpowerlifting-*.csv")[0]
cols = ["Name", "Sex", "Equipment", "Age", "BodyweightKg", "Tested", "Date", "MeetName"]
for L in LIFTS:
    cols += [f"{L}1Kg", f"{L}2Kg", f"{L}3Kg", f"Best3{L}Kg"]

df = pd.read_csv(csv, usecols=cols, low_memory=False)
print(f"Rader i CSV: {len(df):,}")

# Rensing
# Bare klassisk (Raw) og Wraps. Utstyrsløft (single/multi-ply) er nesten en annen sport.
df = df[df.Equipment.isin(["Raw", "Wraps"])]
df = df[df.Sex.isin(["M", "F"]) & df.BodyweightKg.notna()]
df["Date"] = pd.to_datetime(df.Date, errors="coerce")
df = df[df.Date.notna()]
# Samme løfter kan stå flere ganger i samme stevne (flere divisjoner) -> fjern duplikater
df = df.drop_duplicates(["Name", "Date", "MeetName"])
print(f"Etter rensing (Raw/Wraps, deduplisert): {len(df):,}")

# Historikk-features: bruker kun stevner før det aktuelle stevnet
# Sorter på løfter og dato, og bruk shift(1) så vi aldri ser dagens resultat.
df = df.sort_values(["Name", "Date"]).reset_index(drop=True)
g = df.groupby("Name")
df["n_prev_meets"] = g.cumcount()                              # antall tidligere stevner
df["days_since_last"] = (df.Date - g.Date.shift(1)).dt.days    # dager siden forrige stevne

for L in LIFTS:
    best = df[f"Best3{L}Kg"].where(df[f"Best3{L}Kg"] > 0)       # beste godkjente løft i stevnet
    running_best = best.groupby(df.Name).cummax().groupby(df.Name).ffill()
    df[f"prev_best_{L}"] = running_best.groupby(df.Name).shift(1)  # beste før dette stevnet

    att = df[[f"{L}1Kg", f"{L}2Kg", f"{L}3Kg"]]
    made = (att > 0).sum(axis=1)
    tried = att.notna().sum(axis=1)
    made_before = made.groupby(df.Name).cumsum() - made
    tried_before = tried.groupby(df.Name).cumsum() - tried
    df[f"hist_rate_{L}"] = (made_before / tried_before).where(tried_before > 0)

# Historikken er regnet ut fra alle år. Selve treningsradene tar vi fra 2012 og utover.
df = df[df.Date.dt.year >= 2012].reset_index(drop=True)

# Én rad per forsøk
# Negativ vekt i OpenPowerlifting = underkjent forsøk.
def misses(L):
    return (df[[f"{L}1Kg", f"{L}2Kg", f"{L}3Kg"]] < 0).sum(axis=1).to_numpy()

# Bom i løft som kom tidligere i stevnet (rekkefølgen er knebøy -> benk -> markløft)
misses_before = {"Squat": 0, "Bench": misses("Squat"), "Deadlift": misses("Squat") + misses("Bench")}

rows = []
for lift_nr, L in enumerate(LIFTS):
    A = df[[f"{L}1Kg", f"{L}2Kg", f"{L}3Kg"]].to_numpy()
    W, M = np.abs(A), A > 0                      # W = vekt, M = godkjent (True/False)

    # Behold bare løft der alle tre forsøk er registrert og vekten aldri går ned
    ok = ~np.isnan(A).any(axis=1) & (A != 0).all(axis=1)
    ok &= (W[:, 1] >= W[:, 0]) & (W[:, 2] >= W[:, 1])

    for k in range(3):  # forsøk 1, 2, 3
        r = pd.DataFrame({
            "name": df.Name, "year": df.Date.dt.year,
            "lift": lift_nr, "attempt": k + 1,
            "sex": (df.Sex == "M").astype(int), "age": df.Age, "bw": df.BodyweightKg,
            "tested": (df.Tested == "Yes").astype(int), "wraps": (df.Equipment == "Wraps").astype(int),
            "weight": W[:, k],
            "made": M[:, k].astype(int),
            "misses_prior_lifts": misses_before[L],
            "prev_best": df[f"prev_best_{L}"], "hist_rate": df[f"hist_rate_{L}"],
            "n_prev_meets": df.n_prev_meets, "days_since_last": df.days_since_last,
        })
        if k == 0:  # første forsøk: ingen tidligere forsøk i dette løftet
            r["jump_kg"] = np.nan
            r["prev_missed"] = np.nan
            r["misses_this_lift"] = 0
        else:
            r["jump_kg"] = W[:, k] - W[:, k - 1]               # hopp fra forrige forsøk
            r["prev_missed"] = (~M[:, k - 1]).astype(float)    # var forrige forsøk bom?
            r["misses_this_lift"] = (~M[:, :k]).sum(axis=1)    # bom hittil i dette løftet
        rows.append(r[ok])

X = pd.concat(rows, ignore_index=True)

# Relative features: vekten sett i forhold til løfteren selv
X["pct_pr"] = X.weight / X.prev_best          # vekt i forhold til beste tidligere stevneløft
X["weight_bw"] = X.weight / X.bw              # vekt i forhold til kroppsvekt
X["jump_pct"] = X.jump_kg / (X.weight - X.jump_kg)

X.to_parquet(OUT, index=False)
print(f"Forsøksrader: {len(X):,}  |  andel godkjent: {X.made.mean():.3f}")
print(X.groupby(["lift", "attempt"]).made.mean().unstack().round(3))