# Data

Dataene ligger ikke i git fordi filene er for store. Slik får du dem:

## Hvor dataene kommer fra
Alle stevneresultater fra [OpenPowerlifting](https://www.openpowerlifting.org). Vi bruker eksporten fra 3. oktober 2026, lastet ned 7. oktober 2026.

Last ned her: https://openpowerlifting.gitlab.io/opl-csv/files/openpowerlifting-latest.zip

Merk at lenken alltid gir den nyeste versjonen, så du kan få litt nyere data enn oss.

## Slik gjør du det
1. Last ned zip-filen fra lenken over.
2. Pakk den ut i `data/raw/`.
3. Da har du en mappe med en CSV-fil på rundt 790 MB, pluss `README.txt` som forklarer kolonnene.

## Lisens
Dataene er public domain, så de kan brukes fritt. OpenPowerlifting ber likevel om at man nevner dem, så det gjør vi i rapporten.

Dataene inneholder navn på ekte løftere, så vi tar med en kort vurdering av personvern i rapporten.

## Det vi har sjekket
- Litt over 4 millioner rader, én per løfter per stevne.
- Stevner fra 1964 til slutten av september 2026.
- De siste månedene har langt færre rader enn vanlig. Resultater blir nok lagt inn etter hvert, så de nyeste dataene er ikke komplette.
