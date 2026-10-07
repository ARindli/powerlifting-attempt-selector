# Prosjektplan – Forsøksvelger

Planen følger ML-livssyklusen fra forelesning 9 i DAT158 («The ML project lifecycle») og
sjekklisten i Géron, *Hands-On Machine Learning*, Appendix A. Hver fase peker til kapitlet i
rapporten der den skal dokumenteres.

Kryss av underveis. Skriv korte notater om valg og funn i [docs/beslutningslogg.md](docs/beslutningslogg.md)
med en gang. Det er råmaterialet til rapporten.

```
Forstå problemet  →  Data  →  Modellering  →  Deployment
   (rapport 1)      (rapport 2)  (rapport 3)     (rapport 4)
        ↑                                            │
        └──────────── overvåking og nye data ────────┘
```

---

## Fase 0 – Oppsett

- [x] Opprett et offentlig GitHub-repo og push denne mappestrukturen
- [x] Bestem Python-versjon og hvordan miljøet skal gjenskapes (requirements-fil eller conda-miljø)
- [ ] Bestem hva som **ikke** skal i git (rådata, store modellfiler) og hvordan andre likevel kan gjenskape dem
- [ ] Start [docs/kilder.md](docs/kilder.md) og før inn hver kilde (også AI-verktøy) fortløpende

**Ferdig når:** repoet er offentlig, og en annen person kan klone det og forstå strukturen fra README.

---

## Fase 1 – Forstå problemet («big picture») → Rapport kap. 1

Fra forelesningen: *scoping, forstå konteksten, hvilke systemer og prosesser finnes i dag, hvilke
problemer bør og kan løses, gjennomførbarhet, definer mål og metrikker.*

### 1.1 Omfang
- [ ] Formuler problemet i én setning. Hva er input, og hva er output?
- [ ] Hvem er brukeren, og i hvilken situasjon bruker de verktøyet? Hvor mye tid har de?
- [ ] Hvordan løses dette i dag uten ML (treneren, tommelfingerregler, prosent av PR)?
- [ ] Hvorfor er ML et godt verktøy her, og hva kan ML **ikke** løse?
- [ ] Hvilken type ML-problem er det (klassifikasjon, regresjon, …)? Hva er én rad i datasettet?
- [ ] Hvilke deler av systemet er ML, og hvilke er vanlig logikk (f.eks. beslutningslaget)?
- [ ] Hvilke ressurser trengs (maskinvare, tid, personer)?

### 1.2 Metrikker
- [ ] Velg ML-metrikker, og begrunn hvorfor de passer til problemet. Tenk på ubalanse og på at appen viser sannsynligheter.
- [ ] Velg software-metrikker (svartid, oppetid)
- [ ] Definer «business objective»: hva betyr suksess for brukeren? Hvordan kunne det vært målt?
- [ ] Sett et minimum for når prosjektet er en suksess
- [ ] Hvordan henger ML-metrikkene sammen med business-målet?

### 1.3 Gjennomførbarhet
- [ ] Finnes det data med labels? Hvor mye?
- [ ] Er det realistisk å bli ferdig før fristen? Hva er minste versjon som er verdt å levere?
- [ ] Hva er den største risikoen for at prosjektet ikke fungerer, og hvordan kan den sjekkes tidlig?

**Ferdig når:** rapportens kapittel 1 har et førsteutkast.

---

## Fase 2 – Data → Rapport kap. 2

### 2.1 Definer data
- [ ] Hvilke kilder, kolonner og labels trengs? Hva er målvariabelen?
- [ ] Hvor konsistente er labels, og hva kan gjøre dem upålitelige?
- [ ] Lisens og vilkår for datasettet. Personvern og etikk (dataene inneholder navn på ekte personer).

### 2.2 Hent data
- [ ] Last ned dataene og noter versjon og dato
- [ ] Dokumenter nedlastingen så den kan gjentas (se [data/README.md](data/README.md))
- [ ] Verifiser dataene: antall rader, kolonnetyper, manglende verdier, åpenbare feil

### 2.3 Utforsk data (EDA) og feature engineering
- [ ] Lag en kopi eller et utvalg å utforske på, ikke rør testdata
- [ ] Studer fordelinger, manglende verdier og ubalanse i målvariabelen
- [ ] **Levedyktighetssjekk:** finnes det et signal? Hvilket enkelt plott kan vise det?
- [ ] Hvilke features kan bygges? Grupper dem (forsøket, stevnet så langt, historikk, løfteren).
- [ ] For hver feature: er den tilgjengelig **før** forsøket i virkeligheten? Hvis ikke er det lekkasje.
- [ ] Domenekunnskap: hvilke sammenhenger forventer du, og stemmer de med dataene?

### 2.4 Klargjør data
- [ ] Rensing: hva filtreres bort, og hvorfor? Noter hvor mange rader hvert steg fjerner.
- [ ] Håndtering av manglende verdier
- [ ] Skalering og koding, hvis modellene trenger det
- [ ] Bygg stegene som en reproduserbar pipeline (DAG): rådata → renset → split → features → modell
- [ ] **Split:** hvordan skal data deles i trening, validering og test? Hvorfor er en tilfeldig split per rad farlig her?
- [ ] Sjekk at historikk-features bare bruker informasjon fra tidligere stevner

**Ferdig når:** et skript eller en notebook lager et ferdig treningsdatasett fra rådata uten manuelle steg, og kapittel 2 har et utkast.

---

## Fase 3 – Modellering → Rapport kap. 3

### 3.1 Baseline
- [ ] Minst én baseline uten ML (f.eks. gjennomsnittlig godkjentrate per forsøk)
- [ ] En enkel, tolkbar modell
- [ ] Finnes det tall fra andre eller «human level performance» å sammenligne med?

### 3.2 Utforsk ML-modeller (bredde før dybde)
- [ ] Prøv flere modelltyper med standardinnstillinger («no free lunch»)
- [ ] Hold oversikt over alle eksperimenter: modell, features, data, score (se [docs/eksperimentlogg.md](docs/eksperimentlogg.md))
- [ ] Ranger modellene på valideringsdata

### 3.3 Finjuster
- [ ] Hyperparametersøk med kryssvalidering. Hvilken CV-strategi passer når dataene har tid og grupper?
- [ ] Vurder ensembler av de beste modellene
- [ ] Vurder domenekunnskap i modellen (f.eks. monotone begrensninger)
- [ ] Vurder kalibrering av sannsynlighetene

### 3.4 Evaluer og valider
- [ ] Evaluer på testsettet **én gang**, til slutt
- [ ] Rapporter alle metrikker for alle modeller i én tabell
- [ ] Kalibreringsplott
- [ ] Feilanalyse: hvor bommer modellen? Del opp i grupper (løft, forsøksnummer, med og uten historikk).
- [ ] Feature importance og eventuelt ablasjon. Hva betyr resultatet?
- [ ] Bias: fungerer modellen like godt for ulike grupper (kjønn, alder, føderasjon)?
- [ ] Sammenlign ærlig split med naiv split. Hvor mye faller scoren?

### 3.5 Verifiser koden
- [ ] Faste seeds for reproduserbarhet
- [ ] Enkle tester av pipeline-stegene (form og rader, ikke nødvendigvis innhold)
- [ ] Sjekk at modellen oppfører seg fornuftig på håndlagde eksempler (f.eks. tyngre vekt gir aldri høyere sannsynlighet)

**Ferdig når:** endelig modell er valgt og lagret, og kapittel 3 har tabeller og figurer.

---

## Fase 4 – Deployment → Rapport kap. 4

### 4.1 Beslutningslag og nettside
- [ ] Hvordan skal sannsynlighetene gjøres om til anbefalinger? Hva er ML, og hva er regler?
- [ ] Design brukerflyten: hva legger brukeren inn, og hva får de tilbake?
- [ ] Velg web-rammeverk og begrunn valget
- [ ] Input-validering: hva skjer ved ugyldige eller ekstreme verdier?

### 4.2 Sett i drift
- [ ] Velg hosting (f.eks. Hugging Face Spaces eller Render) og begrunn valget
- [ ] Statisk eller dynamisk trening? Begrunn.
- [ ] Deploy, og test hele systemet fra offentlig URL (svartid, feil)
- [ ] Alternativt eller i tillegg: spill inn en skjermvideo

### 4.3 Overvåking og vedlikehold
- [ ] Hva bør overvåkes (datadrift, nye stevner, ytelse over tid)?
- [ ] Hvordan og hvor ofte bør modellen trenes på nytt?
- [ ] Hvordan kunne «business impact» blitt målt etter lansering?
- [ ] Videre arbeid: hva ville du gjort med mer tid?

**Ferdig når:** nettsiden er tilgjengelig, og kapittel 4 har lenke og skjermbilder.

---

## Fase 5 – Innlevering

- [ ] Rapporten er under 3500 ord, og all kursiv instruksjonstekst er slettet
- [ ] Alle kilder er sitert, også AI-verktøy (kapittel 5)
- [ ] README forklarer hvordan alt reproduseres fra bunnen av
- [ ] Repoet er offentlig, og lenken til nettsiden eller videoen ligger i README
- [ ] Test reproduserbarheten: klon repoet på nytt og følg README
- [ ] Lever lenken til repoet på Canvas

---

## Foreslått tidsplan (ca. én uke fulltid)

| Dag | Fokus |
|---|---|
| 1 | Fase 0 og 1, nedlasting av data og levedyktighetssjekk |
| 2 | EDA, rensing og split |
| 3 | Feature engineering og pipeline uten lekkasje |
| 4 | Baselines og bred modellutforsking |
| 5 | Finjustering, kalibrering og evaluering på testsett |
| 6 | Beslutningslag, nettside og deployment |
| 7 | Rapport, README og test av reproduserbarhet |

Skriv rapporten fortløpende. Ikke spar den til dag 7.
