"""Nettsiden. Kjøres med: streamlit run app/app.py"""
from pathlib import Path

import altair as alt
import joblib
import numpy as np
import pandas as pd
import streamlit as st

MODEL_PATH = Path(__file__).parent.parent / "models" / "model.joblib"
LIFTS = {"Knebøy": 0, "Benkpress": 1, "Markløft": 2}
STEP = 2.5        # vektene går i steg på 2,5 kg
N_CANDIDATES = 9  # antall kandidatvekter som vises
ACCENT = "#5B8DEF"

# Hvor mange prosentpoeng lavere sjanse enn den tryggeste vekten hver profil godtar.
# (konservativ, balansert, aggressiv) per forsøksnummer
RISK = {1: (0.01, 0.02, 0.04), 2: (0.02, 0.05, 0.10), 3: (0.05, 0.15, 0.25)}


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


bundle = load_model()
model, FEATURES = bundle["model"], bundle["features"]


def fmt(x):
    """Norsk tallformat: 212.5 -> 212,5"""
    return f"{x:g}".replace(".", ",")


# Utseende: farger og fonter ligger i .streamlit/config.toml, resten her
st.set_page_config(page_title="Forsøksvelger", page_icon="🏋️", layout="wide")
st.html("""<style>
.block-container { max-width: 1200px; padding-top: 5rem; }
h1, h2, h3 { text-transform: uppercase; letter-spacing: .05em; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #1C1F24; border-radius: 14px; }
.brand { display: flex; align-items: center; gap: 12px; font: 700 34px 'Barlow Condensed'; letter-spacing: .04em; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #F4F4F2; margin-right: 4px; }
.dot.orange { background: #F08A4B; }
.sub { color: #A3A9B2; font-size: 14px; margin: 4px 0 8px; }
.num { font: 500 14px 'IBM Plex Mono'; color: #5B8DEF; margin-right: 10px; }
.big { display: flex; gap: 40px; flex-wrap: wrap; align-items: flex-end; }
.big .lbl { font-size: 13px; color: #A3A9B2; }
.big .val { font: 700 60px/1 'Barlow Condensed'; }
.big .val small { font-size: 26px; color: #A3A9B2; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
.card { background: #16191D; border: 1px solid #2C3036; border-radius: 12px; padding: 14px 16px; }
.card.on { border-color: #5B8DEF; background: #232A38; }
.card .name { font: 600 17px 'Barlow Condensed'; letter-spacing: .06em; text-transform: uppercase; }
.card .kg { font: 700 32px/1.1 'Barlow Condensed'; }
.card .d { font-size: 13px; color: #A3A9B2; }
.cands { display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 4px; }
.cand { text-align: center; padding: 8px 2px; border-radius: 8px; border: 1px solid #2C3036; background: #16191D; }
.cand.on { border-color: #5B8DEF; background: #232A38; }
.cand .kg { font: 500 14px 'IBM Plex Mono'; } .cand .pc { font-size: 12px; color: #A3A9B2; }
.cand .tag { font-size: 10px; min-height: 15px; color: #5B8DEF; }
.sees { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.sees div { background: #131518; border-radius: 10px; padding: 10px 14px; }
.sees span { display: block; font-size: 13px; color: #A3A9B2; } .sees b { font: 500 18px 'IBM Plex Mono'; }
.warn { border: 1px solid #F08A4B; border-radius: 10px; padding: 12px 14px; color: #F7B48A; background: #2A1F18; }
.note { font-size: 13px; color: #A3A9B2; }
</style>""")


def heading(num, text):
    st.html(f'<h2 style="margin:0"><span class="num">{num}</span>{text}</h2>')


# Toppen av siden
st.html("""<div class="brand"><span><i class="dot"></i><i class="dot"></i><i class="dot orange"></i></span>FORSØKSVELGER FOR STYRKELØFT</div>
<div class="sub">Sannsynlighet for godkjent løft, lært fra ca. 10 millioner stevneforsøk i OpenPowerlifting</div>""")
st.divider()

left, right = st.columns([1, 1.7], gap="large")

# Venstre kolonne: input
with left:
    with st.container(border=True):
        heading("01", "Løfteren")
        c1, c2 = st.columns(2)
        sex = c1.selectbox("Kjønn", ["Mann", "Kvinne"])
        equipment = c2.selectbox("Utstyr", ["Raw", "Wraps"], format_func=lambda e: "Klassisk (raw)" if e == "Raw" else e)
        age = c1.number_input("Alder", 14, 90, 25)
        bw = c2.number_input("Kroppsvekt (kg)", 40.0, 200.0, 83.0, step=0.5)
        n_meets = c1.number_input("Tidligere stevner", 0, 100, 3)
        tested = c2.selectbox("Testet føderasjon", ["Ja", "Nei"]) == "Ja"

    with st.container(border=True):
        heading("02", "Stevnet så langt")
        lift_name = st.segmented_control("Løft", list(LIFTS), default="Knebøy", width="stretch") or "Knebøy"
        attempt = st.segmented_control("Neste forsøk", [1, 2, 3], default=3, width="stretch",
                                       format_func=lambda a: f"{a}. forsøk") or 3
        pr = st.number_input(f"Beste stevneløft i {lift_name.lower()} (kg) – 0 hvis ingen", 0.0, 500.0, 200.0, step=2.5)

        previous = []  # (vekt, godkjent) for forsøkene som allerede er tatt i dette løftet
        for i in range(attempt - 1):
            c1, c2 = st.columns([1.2, 1.4], vertical_alignment="bottom")
            w = c1.number_input(f"{i + 1}. forsøk (kg)", 20.0, 500.0, 180.0 + 10 * i, step=2.5, key=f"w{i}")
            res = c2.segmented_control("Resultat", ["Godkjent", "Bom"], default="Godkjent",
                                       key=f"r{i}", label_visibility="collapsed") or "Godkjent"
            previous.append((w, res == "Godkjent"))

        misses_prior = 0
        if lift_name != "Knebøy":
            misses_prior = st.number_input("Bom i tidligere løft i dag", 0, 6, 0)
        st.html('<div class="note">Bom i tidligere løft teller med, siden de sier noe om dagsformen.</div>')

# Kandidatvekter og prediksjon
with right:
    if any(b[0] < a[0] for a, b in zip(previous, previous[1:])):
        st.error("Vekten kan ikke senkes fra forrige forsøk.")
        st.stop()

if previous:
    last_w, last_ok = previous[-1]
    start = last_w + STEP if last_ok else last_w    # etter bom kan man ta samme vekt igjen
    step = STEP
else:  # åpningsforsøk: rundt 80–100 % av beste stevneløft
    ref = pr if pr > 0 else bw * {0: 1.6, 1: 1.1, 2: 2.0}[LIFTS[lift_name]]
    start = round(0.8 * ref / STEP) * STEP
    step = max(STEP, round(0.2 * ref / (N_CANDIDATES - 1) / STEP) * STEP)
weights = start + step * np.arange(N_CANDIDATES)


def make_features(w):
    """Lag de samme featurene som modellen er trent på."""
    d = pd.DataFrame({"weight": w})
    d["lift"], d["attempt"] = LIFTS[lift_name], attempt
    d["sex"], d["age"], d["bw"] = int(sex == "Mann"), age, bw
    d["tested"], d["wraps"] = int(tested), int(equipment == "Wraps")
    d["weight_bw"] = w / bw
    d["pct_pr"] = w / pr if pr > 0 else np.nan
    d["jump_kg"] = w - previous[-1][0] if previous else np.nan
    d["jump_pct"] = d.jump_kg / previous[-1][0] if previous else np.nan
    d["prev_missed"] = float(not previous[-1][1]) if previous else np.nan
    d["misses_this_lift"] = sum(not ok for _, ok in previous)
    d["misses_prior_lifts"] = misses_prior
    d["n_prev_meets"] = n_meets
    d["hist_rate"] = np.nan          # ukjent i appen, modellen håndterer manglende verdier
    d["days_since_last"] = np.nan
    return d[FEATURES]


p = model.predict_proba(make_features(weights))[:, 1]

made = [w for w, ok in previous if ok]
best_made = max(made) if made else None
gain = p * (weights - best_made) if best_made else None   # forventet gevinst i kg


# Beslutningslag (ikke ML): tre profiler basert på hvor mye risiko man godtar
def heaviest_within(drop):
    """Tyngste vekt der sjansen er høyst `drop` lavere enn for den letteste kandidaten."""
    return int(np.where(p >= p[0] - drop)[0][-1])


bomb_risk = attempt == 3 and not made
if bomb_risk:  # to bom: et nytt bom betyr ingen total, så velg trygt
    picks = {"Anbefalt": heaviest_within(0.02)}
    desc = {"Anbefalt": "Trygt valg når et nytt bom betyr ingen total"}
else:
    drops = RISK[attempt]
    picks = dict(zip(["Konservativ", "Balansert", "Aggressiv"], map(heaviest_within, drops)))
    desc = {name: f"Maks {d * 100:.0f} prosentpoeng lavere sjanse enn {fmt(weights[0])} kg"
            for name, d in zip(picks, drops)}

# Høyre kolonne: resultat
with right, st.container(border=True):
    heading("03", f"Velg {attempt}. forsøk i {lift_name.lower()}")
    if bomb_risk:
        st.html('<div class="warn">To underkjente forsøk: et nytt bom betyr ingen total. Forslaget er derfor konservativt.</div>')

    big = st.empty()  # fylles inn under, når vekten er valgt
    default = list(picks.values())[min(1, len(picks) - 1)]
    sel = st.select_slider("Velg vekt", options=list(range(N_CANDIDATES)), value=default,
                           format_func=lambda i: f"{fmt(weights[i])} kg")

    big.html(f"""<div class="big">
      <div><div class="lbl">Valgt vekt</div><div class="val">{fmt(weights[sel])}<small> kg</small></div></div>
      <div><div class="lbl">Sjanse for godkjent</div><div class="val" style="color:{ACCENT}">{p[sel]:.0%}</div></div>
      <div><div class="lbl">Forventet gevinst</div><div class="val" style="font-size:38px">
        {'–' if gain is None else '+' + fmt(round(gain[sel], 1)) + ' kg'}</div></div></div>""")

    # Kurve: sannsynlighet mot vekt, med forslagene markert
    df = pd.DataFrame({"Vekt": weights, "Sjanse": p})
    base = alt.Chart(df).encode(x=alt.X("Vekt:Q", title="Vekt (kg)", scale=alt.Scale(zero=False)),
                                y=alt.Y("Sjanse:Q", title="Sjanse for godkjent", scale=alt.Scale(domain=[0, 1]),
                                        axis=alt.Axis(format="%")))
    marks = pd.DataFrame({"Vekt": weights[list(picks.values())], "Sjanse": p[list(picks.values())]})
    chart = (base.mark_area(color=ACCENT, opacity=0.12)
             + base.mark_line(color=ACCENT, strokeWidth=3)
             + alt.Chart(marks).mark_point(color=ACCENT, size=80, filled=False, strokeWidth=2).encode(x="Vekt:Q", y="Sjanse:Q")
             + alt.Chart(df.iloc[[sel]]).mark_point(color=ACCENT, size=220, filled=True).encode(x="Vekt:Q", y="Sjanse:Q"))
    st.altair_chart(chart.properties(height=240).configure_view(stroke=None)
                    .configure_axis(gridColor="#2C3036", domainColor="#3A3F47", labelColor="#8B929C",
                                    titleColor="#A3A9B2"), use_container_width=True)

    # Kandidatvekter
    tag = {i: name for name, i in reversed(list(picks.items()))}
    st.html('<div class="cands">' + "".join(
        f'<div class="cand {"on" if i == sel else ""}"><div class="kg">{fmt(w)}</div>'
        f'<div class="pc">{p[i]:.0%}</div><div class="tag">{tag.get(i, "")}</div></div>'
        for i, w in enumerate(weights)) + "</div>")

    # Profilkort
    st.html('<div class="cards">' + "".join(
        f'<div class="card {"on" if i == sel else ""}"><div class="name">{name}</div>'
        f'<div class="kg">{fmt(weights[i])} kg</div><div>{p[i]:.0%} sjanse</div><div class="d">{desc[name]}</div></div>'
        for name, i in picks.items()) + "</div>")

    # Hva modellen ser for valgt vekt
    jump = "åpningsforsøk" if not previous else (
        "ingen godkjente ennå" if best_made is None
        else f"+{fmt(weights[sel] - best_made)} kg ({(weights[sel] - best_made) / best_made:.1%})".replace(".", ","))
    st.html(f"""<h3 style="font-size:15px;margin:6px 0 0">Dette ser modellen for valgt vekt</h3><div class="sees">
      <div><span>Andel av beste stevneløft</span><b>{f"{weights[sel] / pr:.0%}" if pr > 0 else "ingen historikk"}</b></div>
      <div><span>Hopp fra siste godkjente</span><b>{jump}</b></div>
      <div><span>Bom hittil i stevnet</span><b>{misses_prior + sum(not ok for _, ok in previous)}</b></div></div>
      <div class="note">Modellen ser bare det som står i resultatlistene. Den vet ikke hvordan oppvarmingen gikk,
      og den har lært av vekter løftere selv valgte, så uvanlig store hopp er usikre. Bruk den som et ekstra
      innspill, ikke som fasit.</div>""")

st.divider()
