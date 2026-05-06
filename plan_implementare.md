# Plan de Prognoza si Optimizare a Cursului Valutar PLN (Zlotul Polonez)

Acest document descrie arhitectura și pașii necesari pentru dezvoltarea modelului de predicție cu optimizare aplicată prin biblioteca Optuna, pe baza datelor reale BNR pentru deviza PLN.

## Obiectiv

Refactorizarea codului actual și integrarea unui model predictiv bazat pe algoritmi non-liniari (XGBoost) capabil să prevadă cursul de schimb PLN/RON pentru ziua următoare. Inima proiectului va fi o rutină Optuna care găsește hiperparametrii maximi pentru minimizarea erorii medii absolute (MAE). Proiectul va fi clean-code, bine structurat și pregătit pentru evaluarea universitară.

## Pași propuși de implementare

Vom crea următoarele module sub acest folder:

### 1. `scraper.py`
Refactorizăm script-ul original pentru a fi mai robust și țintit spre **PLN**:
- Extragerea specifică a PLN folosind Playwright.
- Îmbunătățirea curățeniei codului și structurarea acestuia pe funcții clare.

### 2. `model.py`
Partea Machine Learning a temei. Aici propunem **două variante diferite de optimizare** pentru a satisface criteriile analizate:
- **Varianta 1 (Optuna):** Căutare inteligentă a spațiului de parametri. Optuna va scana eficient prin `n_estimators`, `learning_rate` și `max_depth` ai modelului XGBoost generând trials. Este modernă și rapidă.
- **Varianta 2 (GridSearchCV):** Căutare exhaustivă tradițională folosind Scikit-Learn. Acesta va testa o matrice finită predefinită de parametri prin validare încrucișată (Time Series Split). Foarte robustă dar teoretic mai lentă.

Pentru ambele variante:
- Se va face feature engineering cu lag-uri (t-1, t-7).
- Se va exporta modelul final.

### 3. `main.py`
Fișierul orchestrator („Entrypoint”) ce demonstrează soluția ca un proiect compact:
- Rularea inițială a scraper-ului.
- Invocarea fluxului de prelucrare a datelor și antrenare cu tuning. (Limitat la pragul de 30-50 de teste în Optuna pentru operativitate și reducerea timpului de rulare).
- Generarea metricilor comparative pentru fișierul `.py` care stă la baza proiectului.
