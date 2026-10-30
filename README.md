# Forsøksvelger for styrkeløft

Står du i et styrkeløftstevne og lurer på hva du skal melde neste forsøk? Legg inn hvordan dagen har gått, så får du sjansen for godkjent løft på ulike vekter, og tre forslag, konservativ, balansert og aggressivt.

Modellen er trent på rundt 10 millioner forsøk fra OpenPowerlifting.

**Prøv den her:** https://powerlifting-attempt-selector.streamlit.app

**Rapporten:** [rapport/DAT158 Rapport - Forsøksvelger.docx](rapport/DAT158%20Rapport%20-%20Fors%C3%B8ksvelger.docx)

Laget i DAT158 Maskinlæring på HVL.

## Kjør det selv

```bash
conda env create -f environment.yml
conda activate forsoksvelger
```

Last ned [dataene](https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip) og pakk dem ut i `data/raw/`. Så:

```bash
python src/prepare_data.py
python src/train.py
streamlit run app/app.py
```
