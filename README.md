# BNR Agentic Dashboard: Prognoză valutară PLN/RON

Acest proiect este o aplicație full-stack construită pentru a prezice cursul valutar PLN (Zlotul Polonez) în raport cu RON. Arhitectura combină un dashboard interactiv, un model de Machine Learning optimizat și un asistent AI bazat pe "Tool Calling", care extrage și interpretează date financiare în timp real.

## Funcționalități principale

* **Asistent Agentic BNR:** Un chatbot conectat la Groq API. Acesta interpretează comenzile în limbaj natural, decide singur când să ruleze funcții din backend prin Tool Calling și oferă context pe baza datelor extrase.
* **Machine Learning Forecast:** Un model XGBoost Regressor optimizat riguros prin 100 de trial-uri în Optuna. Am aplicat tehnici de feature engineering, incluzând rolling means și momentum, pentru a crește precizia.
* **Scraping automat:** Un script Playwright integrat care extrage automat datele istorice direct de pe cursbnr.ro.
* **Interfață grafică:** Un dashboard construit în React (Vite) cu grafice Recharts și suport nativ pentru dark mode.

## Tehnologii utilizate

* **Backend:** Python, FastAPI, Uvicorn, Groq API
* **Frontend:** React, Vite, Recharts, Vanilla CSS
* **AI / ML:** XGBoost, Optuna, Scikit-learn, Pandas
* **Web scraping:** Playwright

## Instalare și rulare

Procesul de rulare este complet automatizat pentru a fi ușor de testat. Nu este necesară introducerea manuală a comenzilor.

1. Rulați fișierul `start_app.bat`.
2. Scriptul va verifica și instala automat toate dependențele necesare pentru mediile Python și Node.js.
3. La finalizarea instalării, apăsați tasta **Y** pentru a porni ambele servere în fundal.
4. Aplicația se va deschide automat în browserul implicit la adresa: http://localhost:5173.

> **Notă:** La prima rulare, descărcarea dependențelor pentru React (`node_modules`) poate dura 1-2 minute, în funcție de conexiunea la internet.

## Structura proiectului

```text
├── agentic_docs/          # Documentație tehnică și jurnale de dezvoltare
├── date_extrase/          # Baza de date CSV și modelul antrenat (.pkl)
├── frontend/              # Codul sursă pentru interfața React
├── src/
│   ├── api/               # Serverul FastAPI și logica asistentului (server.py)
│   └── core/              # Pipeline ML, scraper BNR și antrenare Optuna (model.py)
├── start_app.bat          # Scriptul automat de instalare și rulare
└── .env                   # Variabile de mediu
```

## Metrici de performanță ML

Modelul XGBoost utilizează Time Series Cross-Validation și este evaluat pe baza următoarelor metrici:
* **MAE** (Eroarea Medie Absolută)
* **RMSE** (Root Mean Squared Error)
* **MAPE** (Mean Absolute Percentage Error)
---
**Autor:** Cristian Antonescu<br>
**Program:** Master SIIPA, Anul 1<br>
**Curs:** Aplicații ale inteligenței artificiale în economie<br>
**Instructor:** Teodor Ștefan BÎLDEA
