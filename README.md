# Forsøksvelger

*[Én til to setninger om hva produktet gjør og hvem det er for.]*

DAT158 Maskinlæring – innlevering 2, Høgskulen på Vestlandet.

**Nettside:** [lenke] · **Video:** [lenke] · **Rapport:** [rapport/rapport.md](rapport/rapport.md)

## Innhold i repoet

| Mappe | Innhold |
|---|---|
| [`data/`](data/) | Rådata (ikke i git) og prosesserte data. Se [data/README.md](data/README.md) for nedlasting. |
| [`notebooks/`](notebooks/) | Utforsking, EDA og eksperimenter |
| [`src/`](src/) | Gjenbrukbar kode: datapipeline, features, trening og evaluering |
| [`models/`](models/) | Lagrede modeller (store filer ikke i git) |
| [`app/`](app/) | Nettsiden og API-et |
| [`rapport/`](rapport/) | Rapporten og figurene som brukes i den |
| [`docs/`](docs/) | Beslutningslogg, eksperimentlogg og kildeliste |

Arbeidsplanen ligger i [PLAN.md](PLAN.md).

## Reproduser resultatene

*[Fylles ut underveis. Noen som aldri har sett prosjektet skal kunne følge stegene fra et tomt
oppsett til kjørende nettside.]*

1. Miljø (Python 3.12):
   ```bash
   conda env create -f environment.yml
   conda activate forsoksvelger
   ```
   Uten conda: lag et virtuelt miljø med Python 3.12 og kjør `pip install -r requirements.txt`.
2. Data: *[hvordan laste ned]*
3. Prosessering: *[hvilket skript eller notebook, og hva det produserer]*
4. Trening og evaluering: *[kommando, forventet tid, hvor resultatene havner]*
5. Kjør nettsiden lokalt: *[kommando]*
6. Deployment: *[hvordan siden er satt i drift]*

## Data og lisens

*[Datakilde, versjon og lisens.]*

## Kilder

Se [docs/kilder.md](docs/kilder.md).
