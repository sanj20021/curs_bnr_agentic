# BNR Agentic Dashboard - Prognoză Valutară PLN/RON 📊🤖

Aplicație Full-Stack avansată pentru predicția cursului valutar PLN (Zlotul Polonez) față de RON. Proiectul include un **Dashboard Interactiv**, un **Model XGBoost optimizat (Optuna)** și un **Asistent Agentic AI** (Llama 3.3) capabil să extragă și să interpreteze datele financiare în timp real folosind arhitectură de "Tool Calling".

## ✨ Funcționalități Principale

- 🤖 **Asistent Agentic BNR** - Chatbot inteligent integrat cu Groq API. Interpretează limbajul natural, decide singur când să ruleze funcții de backend (Tool Calling) și oferă previziuni contextuale.
- 📉 **Machine Learning Forecast** - Model XGBoost Regressor optimizat hiperparametric cu 100 de trial-uri Optuna + feature engineering (rolling means, momentum).
- 🕸️ **Scraping Automat** - Extragere automată a datelor istorice de la cursbnr.ro folosind Playwright.
- 🎨 **Dashboard Premium** - Interfață grafică modernă "Glassmorphism", creată în React (Vite) + Recharts, cu suport pentru dark mode.

## ⚙️ Tehnologii Utilizate

- **Backend:** Python, FastAPI, Uvicorn, Groq API (LLM Tool Calling)
- **Frontend:** React, Vite, Recharts, Lucide Icons, Vanilla CSS
- **AI / ML:** XGBoost, Optuna, Scikit-learn, Pandas
- **Web Scraping:** Playwright

## 🚀 Instalare și Rulare Automată (Plug & Play)

Rularea aplicației a fost complet automatizată pentru o evaluare rapidă și ușoară. Nu este nevoie să rulați comenzi manuale!

1. Deschideți fișierul **`start_app.bat`** (dublu-click).
2. Scriptul va verifica și instala automat dependențele necesare pentru Python și Node.js.
3. Odată finalizat, apăsați tasta **Y** pentru a porni cele două servere în fundal.
4. Aplicația se va deschide automat în browser la adresa: `http://localhost:5173`.

> **Notă:** La prima rulare, descărcarea modulelor React (`node_modules`) poate dura ~1-2 minute în funcție de conexiune.

## 📂 Structura Proiectului

```text
├── agentic_docs/          # Jurnale, planuri tehnice și documentație AI rezultată în dezvoltare
├── date_extrase/          # Baza de date CSV cu istoricul cursului și modelul antrenat (.pkl)
├── frontend/              # Codul sursă pentru interfața React
├── src/
│   ├── api/               # Serverul FastAPI și logica Asistentului Agentic (server.py)
│   └── core/              # Pipeline ML, scraper BNR și antrenare Optuna (model.py)
├── start_app.bat          # Scriptul automat de instalare și rulare
└── .env                   # Variabile de mediu (Cheia API implicită pentru LLM)
```

## 📊 Metrici de Performanță ML

Modelul XGBoost utilizează Time Series Cross-Validation și este evaluat riguros după:
- **MAE** (Eroarea Medie Absolută)
- **RMSE** (Root Mean Squared Error)
- **MAPE** (Mean Absolute Percentage Error)

---

**Autor:** Cristian Antonescu  
**Master:** SIIPA, UNITBV, An 1  
**Curs:** Aplicații ale inteligenței artificiale în economie  
**Instructor:** Teodor Ștefan BÎLDEA  
