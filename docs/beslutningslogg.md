# Beslutningslogg

Skriv ned hvert viktig valg mens du tar det. Dette er råmaterialet til rapporten, som skal vise
hvor mye arbeid som gikk med til å planlegge og designe løsningen.

Format: **dato – valg – alternativer som ble vurdert – begrunnelse – konsekvens/funn**

---

## Fase 1 – Problem
Bruker er i et konkurranse senario og trenger forslag til vekt på neste forsøk.
Legger inn data på hva som er gjort hittil, får ut data på konservativt, balansert og aggressivt forsøk.Basert på historisk data av hva andre løftere i samme situasjon har gjort.
I dag uten ML så man gjøre antagelser på stedet og gjette på hva man klarer på neste.
ML modellen kan gi et ekstra perspektiv på hva som historisk sett har funket og ikke funket og gi en sansynelighetsberegning på hvor stort hopp som vil gå.

### Metrikker
- Kalibrering er viktigst: prosenten brukeren ser må faktisk stemme. Sier appen 70 %, skal omtrent 70 % av slike forsøk bli godkjent.
- Accuracy passer ikke: ca. 77 % av forsøkene blir godkjent, så en modell som alltid sier «godkjent» ser god ut uten å være nyttig.
- I et stevne har man 1 minutt etter et forsøk på å melde neste vekt. Appen må derfor svare på noen få sekunder, og brukeren må ha lite å skrive inn under selve stevnet.

## Fase 2 – Data

## Fase 3 – Modellering

## Fase 4 – Deployment
- Fra fase 1: bare 1 minutt til å melde neste vekt. Det meste (løfterinfo, beste løft) bør fylles inn før stevnet, så det bare er forrige vekt og godkjent/underkjent som legges inn underveis. Forslagene må være lette å lese raskt.
