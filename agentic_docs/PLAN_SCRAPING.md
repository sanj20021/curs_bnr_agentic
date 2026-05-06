# Plan de Scraping - Extragere Date BNR

## Obiectiv
Extragerea automata a seriei istorice a cursului valutar PLN/RON de pe site-ul https://www.cursbnr.ro/curs-valutar-bnr, incepand cu data de 01/01/2020.

## Abordare aleasa
Am ales sa folosesc **Playwright** (browser headless) in locul requests + BeautifulSoup deoarece site-ul cursbnr.ro foloseste JavaScript pentru a incarca datele in tabel dupa selectarea valutei si a datei de start.

## Pasi de implementare

1. **Lansare browser headless** - Playwright deschide un browser Chromium in mod headless
2. **Navigare** - accesam URL-ul https://www.cursbnr.ro/curs-valutar-bnr
3. **Selectare valuta** - selectam PLN din dropdown-ul `<select name="currency">`
4. **Setare data de start** - modificam campul `input[name="dataStart"]` la valoarea `01/01/2020`
5. **Submit formular** - trimitem formularul pentru a obtine datele istorice
6. **Asteptare randare** - asteptam ca tabelul `#table-currencies` sa fie vizibil si sa se incarce complet (timeout 2 secunde aditional)
7. **Extragere HTML tabel** - preluam HTML-ul interior al tabelului
8. **Parsare cu pandas** - folosim `pd.read_html()` pentru a citi tabelul intr-un DataFrame
9. **Salvare CSV** - exportam datele in format CSV cu encoding `utf-8-sig`

## Dependente
- `playwright` - automatizare browser
- `pandas` - parsare tabel HTML si export CSV

## Rezultat
Fisierul CSV generat contine doua coloane: `Data` (format DD.MM.YYYY) si cursul valutar PLN.
Datele sunt salvate in `date_extrase/istoric_curs_pln.csv`.
