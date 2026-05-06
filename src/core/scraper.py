from playwright.sync_api import sync_playwright
import pandas as pd
from io import StringIO
import os

def scrape_curs_bnr(currency_code="PLN", output_dir="."):
    """
    Extrage istoricul cursului valutar BNR pentru o anumită monedă (implicit PLN).
    Folosește Playwright pentru a naviga pe site și a extrage tabelul cu date istorice.
    
    Returnează:
        pd.DataFrame: DataFrame conținând datele parcurse (Data, Curs, etc.).
    """
    url = "https://www.cursbnr.ro/curs-valutar-bnr"
    
    with sync_playwright() as p:
        print(f"Pornim browser-ul pentru a obtine datele {currency_code}...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto(url)
        page.select_option("select[name='currency']", value=currency_code)
        
        # Setăm data de start dorită, de exemplu pentru un istoric relevant (01/01/2020)
        page.evaluate("document.querySelector('input[name=\"dataStart\"]').value = '01/01/2020'")
        page.evaluate("document.querySelector('input[name=\"dataStart\"]').form.submit()")
        
        page.wait_for_selector("table#table-currencies")
        page.wait_for_timeout(2000)  # Așteptăm pentru a ne asigura că randează complet tabelul HTML
        
        table_html = page.inner_html("table#table-currencies")
        table_html_full = f'<table id="table-currencies">{table_html}</table>'
        
        lista_tabele = pd.read_html(StringIO(table_html_full))
        
        if lista_tabele:
            df = lista_tabele[0]
            fisier_csv = os.path.join(output_dir, f"istoric_curs_{currency_code.lower()}.csv")
            df.to_csv(fisier_csv, index=False, encoding="utf-8-sig")
            print(f"Extragere completa! Au fost extrase {len(df)} intrari.")
            print(f"Datele au fost salvate local: {fisier_csv}")
            browser.close()
            return df
        else:
            print("Eroare la parsarea tabelului.")
            browser.close()
            return None

if __name__ == "__main__":
    df_pln = scrape_curs_bnr("PLN")
